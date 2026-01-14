
import pytest
import os
import yaml
from src.core.schema.loader import SchemaLoader, ProtocolSchema, NeuroOpsConfigError

class TestSchemaLoader:
    
    def test_load_basic_schema(self, tmp_path):
        """Test loading a single schema file."""
        config_file = tmp_path / "basic.yaml"
        config_data = {
            "protocol_name": "Test Protocol",
            "thresholds": {"snr_min": 10.0}
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
            
        loader = SchemaLoader()
        schema = loader.load(str(config_file))
        
        assert isinstance(schema, ProtocolSchema)
        assert schema.protocol_name == "Test Protocol"
        assert schema.thresholds.snr_min == 10.0
        
    def test_schema_inheritance(self, tmp_path):
        """Test that project schema successfully inherits and overrides organization defaults."""
        # 1. Create Org Defaults
        org_file = tmp_path / "org_defaults.yaml"
        org_data = {
            "protocol_name": "Org Default",
            "thresholds": {"snr_min": 5.0, "motion_max_mm": 2.0},
            "policies": [{"name": "CheckA", "action": "WARN"}]
        }
        with open(org_file, "w") as f:
            yaml.dump(org_data, f)
            
        # 2. Create Project Override referencing Org Defaults
        proj_file = tmp_path / "project.yaml"
        proj_data = {
            "_base": str(org_file),
            "protocol_name": "Project Specific",
            "thresholds": {"snr_min": 8.0} # Override ONE value
        }
        with open(proj_file, "w") as f:
            yaml.dump(proj_data, f)
            
        # 3. Load
        loader = SchemaLoader()
        schema = loader.load(str(proj_file))
        
        # 4. verify
        # Name should be overridden
        assert schema.protocol_name == "Project Specific"
        # snr_min should be overridden (8.0)
        assert schema.thresholds.snr_min == 8.0
        # motion_max_mm should be inherited (2.0)
        assert schema.thresholds.motion_max_mm == 2.0
        # Policies should be inherited
        assert len(schema.policies) == 1
        assert schema.policies[0]["name"] == "CheckA"

    def test_invalid_schema_structure(self, tmp_path):
        """Test that invalid keys or types raise ValidationErrors (via Pydantic)."""
        bad_file = tmp_path / "bad.yaml"
        # Invalid: snr_min should be float/int, not string "high" (unless castable, but here checking logic)
        # Actually Pydantic casts. Let's try value validation.
        bad_data = {
            "thresholds": {"snr_min": -5.0} # Must be positive
        }
        with open(bad_file, "w") as f:
            yaml.dump(bad_data, f)
            
        loader = SchemaLoader()
        with pytest.raises(NeuroOpsConfigError):
            loader.load(str(bad_file))

    def test_missing_file(self):
        loader = SchemaLoader()
        with pytest.raises(NeuroOpsConfigError):
            loader.load("non_existent_file.yaml")
