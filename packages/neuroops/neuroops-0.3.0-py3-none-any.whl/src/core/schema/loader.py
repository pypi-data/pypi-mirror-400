"""
Module A: Schema Engine (FR-02)
Hierarchical configuration system supporting organization-level defaults
with project-specific overrides.

Architecture Note: This abstraction allows Data Managers to define global policies
while Principal Investigators can customize thresholds per study without code changes.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
import yaml


class NeuroOpsConfigError(Exception):
    """Raised when configuration is invalid or cannot be loaded."""
    pass


class ValidationThresholds(BaseModel):
    """Quality check thresholds - all configurable via Schema."""
    # FR-07: Quality Checks (Soft Fail)
    snr_min: float = Field(default=5.0, description="Minimum acceptable SNR")
    motion_max_mm: float = Field(default=2.0, description="Max framewise displacement (mm)")
    flatline_std_threshold: float = Field(default=1e-15, description="Std below this = dead channel")
    flatline_max_ratio: float = Field(default=0.5, description="Max ratio of flat samples")
    
    # NFR-01: Performance thresholds
    max_validation_time_sec: float = Field(default=5.0, description="Max time for 1GB file validation")
    
    from pydantic import field_validator
    
    @field_validator('snr_min', 'motion_max_mm', 'max_validation_time_sec')
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Threshold must be positive")
        return v


class FileConstraints(BaseModel):
    """FR-01: Protocol Definition - File format constraints."""
    allowed_extensions: List[str] = Field(
        default=[".nii", ".nii.gz", ".fif", ".edf", ".vhdr"],
        description="Valid file extensions for this protocol"
    )
    required_dimensions: Optional[Dict[str, int]] = Field(
        default=None,
        description="Required dimensions (e.g., {'x': 256, 'y': 256})"
    )
    min_resolution_mm: Optional[float] = Field(
        default=None,
        description="Minimum spatial resolution in mm"
    )
    max_resolution_mm: Optional[float] = Field(
        default=None,
        description="Maximum spatial resolution in mm"
    )
    required_header_fields: List[str] = Field(
        default=[],
        description="Header fields that must be present"
    )
    required_header_values: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Header fields that must match specific values"
    )


class ProtocolSchema(BaseModel):
    """
    Root schema model representing a complete validation protocol.
    Supports FR-02: Inheritance Model via _base field.
    """
    # Metadata
    schema_version: str = Field(default="1.0", description="Schema format version")
    protocol_name: str = Field(default="default", description="Human-readable protocol name")
    protocol_id: Optional[str] = Field(default=None, description="Unique identifier")
    
    # Inheritance
    # Inheritance
    # Rename to avoid Pydantic collision with private attributes, but map from YAML '_base'
    base_schema: Optional[str] = Field(default=None, alias="_base", description="Path to parent schema")
    
    # Constraints
    thresholds: ValidationThresholds = Field(default_factory=ValidationThresholds)
    file_constraints: FileConstraints = Field(default_factory=FileConstraints)
    
    # Policies (from existing default_policy.yaml)
    policies: List[Dict[str, Any]] = Field(default=[], description="Named policy rules")
    
    model_config = ConfigDict(extra='allow')


class SchemaLoader:
    """
    FR-02: Hierarchical Configuration Loader.
    
    Resolution order:
    1. Load base organization schema (if _base specified)
    2. Deep merge project schema on top
    3. Validate against ProtocolSchema model
    
    Why: Enables clinical trials to enforce baseline standards while
    allowing per-site customization without forking config files.
    """
    
    def __init__(self, default_org_schema_path: Optional[str] = None):
        """
        Initialize loader with optional default organization schema.
        
        Args:
            default_org_schema_path: Path to fallback organization schema
        """
        self.default_org_schema = default_org_schema_path
        self._cache: Dict[str, ProtocolSchema] = {}
    
    def load(
        self, 
        project_path: str, 
        org_path: Optional[str] = None
    ) -> ProtocolSchema:
        """
        Load and merge hierarchical configuration.
        
        Args:
            project_path: Path to project-specific schema YAML
            org_path: Optional path to organization schema (overrides default)
            
        Returns:
            Merged ProtocolSchema
            
        Raises:
            NeuroOpsConfigError: If schema is invalid or unreadable
        """
        # Load project schema
        project_config = self._load_yaml(project_path)
        
        # Determine base schema path
        # Use .get("_base") on the raw dict, as it hasn't been validated yet
        base_path = project_config.get("_base") or org_path or self.default_org_schema
        
        # Load and merge if base exists
        if base_path:
            if not os.path.isabs(base_path):
                # Resolve relative to project schema location
                base_path = str(Path(project_path).parent / base_path)
            
            if os.path.exists(base_path):
                base_config = self._load_yaml(base_path)
                merged = self._deep_merge(base_config, project_config)
            else:
                # Base specified but not found - warn but continue
                merged = project_config
        else:
            merged = project_config
        
        # Validate against Pydantic model
        try:
            return ProtocolSchema(**merged)
        except Exception as e:
            raise NeuroOpsConfigError(f"Invalid schema: {e}")

    def load_or_infer(
        self,
        project_path: Optional[str],
        data_file_path: Optional[str] = None
    ) -> ProtocolSchema:
        """
        FR-19: Loads schema from YAML if provided, otherwise infers from BIDS.
        """
        # 1. Explicit Config
        if project_path and os.path.exists(project_path):
            return self.load(project_path)
            
        # 2. BIDS Autoconfiguration
        if data_file_path:
            from .bids import BIDSInterpreter
            interpreter = BIDSInterpreter()
            if interpreter.detect_bids_root(data_file_path):
                return interpreter.infer_schema_for_file(data_file_path)
        
        # 3. Fallback to Default
        return ProtocolSchema(protocol_id="default-fallback")
    
    def _load_yaml(self, path: str) -> Dict[str, Any]:
        """Safely load YAML file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f) or {}
            return content
        except FileNotFoundError:
            raise NeuroOpsConfigError(f"Schema file not found: {path}")
        except yaml.YAMLError as e:
            raise NeuroOpsConfigError(f"Invalid YAML in {path}: {e}")
    
    def _deep_merge(
        self, 
        base: Dict[str, Any], 
        override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        Override values take precedence. Lists are replaced, not concatenated.
        
        Args:
            base: Base configuration dict
            override: Override configuration dict
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key == "_base":
                # Don't propagate _base to merged result
                continue
            
            if (
                key in result 
                and isinstance(result[key], dict) 
                and isinstance(value, dict)
            ):
                # Recursive merge for nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override value
                result[key] = value
        
        return result
    
    def get_thresholds(self, schema: ProtocolSchema) -> ValidationThresholds:
        """Extract validation thresholds from schema."""
        return schema.thresholds
    
    def get_file_constraints(self, schema: ProtocolSchema) -> FileConstraints:
        """Extract file constraints from schema."""
        return schema.file_constraints


# Convenience function for quick loading
def load_schema(
    project_path: str, 
    org_path: Optional[str] = None
) -> ProtocolSchema:
    """
    Load a protocol schema with hierarchical inheritance.
    
    Example:
        schema = load_schema("config/my_study.yaml", "config/org_defaults.yaml")
        max_motion = schema.thresholds.motion_max_mm
    """
    loader = SchemaLoader()
    return loader.load(project_path, org_path)
