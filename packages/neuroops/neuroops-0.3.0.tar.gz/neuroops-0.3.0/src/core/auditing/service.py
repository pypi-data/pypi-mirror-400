from typing import List, Dict, Any
from src.ports.base import NeuroSource
from src.core.reporting.models import AuditReport, Status
from .policies import AuditPolicy, SubjectMismatchPolicy, SignalFlatlinePolicy

class IntegrityAuditor:
    """
    Service that orchestrates the Policy Engine.
    Reads rules from a Dict (parsed YAML) and applies them.
    """
    def __init__(self, config: Dict[str, Any]):
        self.policies: List[AuditPolicy] = []
        self._load_policies(config)

    def _load_policies(self, config: Dict[str, Any]):
        """Dynamically instantiates policies based on 'name' field in YAML."""
        policy_list = config.get("policies", [])
        
        # Mapping String -> Class
        # In a larger app, we'd use auto-discovery/registry
        registry = {
            "SubjectMismatch": SubjectMismatchPolicy,
            "SignalFlatline": SignalFlatlinePolicy
        }
        
        for rule in policy_list:
            name = rule.get("name")
            # action = rule.get("action", "WARN") # Unused for now
            
            if name in registry:
                try:
                    policy_cls = registry[name]
                    policy = policy_cls()
                    
                    # If policy has configurable threshold, set it
                    # (Simplified injection for MVP)
                    if name == "SignalFlatline" and "threshold" in rule:
                         # For a real system, we'd explicitly pass config to __init__
                         pass
                    
                    self.policies.append(policy)
                except Exception as e:
                    print(f"Failed to load policy {name}: {e}")

    def evaluate(self, source_a: NeuroSource, source_b: NeuroSource) -> AuditReport:
        all_issues = []
        
        for policy in self.policies:
            issues = policy.check(source_a, source_b)
            all_issues.extend(issues)
            
        # Determine overall status
        status = Status.PASS
        for i in all_issues:
            if i.severity == Status.FAIL:
                status = Status.FAIL
                break
            if i.severity == Status.WARN:
                status = Status.WARN
        
        return AuditReport(
            status=status,
            issues=all_issues
        )
