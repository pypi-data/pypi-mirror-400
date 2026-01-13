"""
Core validation engine for SAP configurations
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
from enum import Enum

from sap_config_guard.core.schema import ConfigSchema
from sap_config_guard.core.loader import ConfigLoader


class ValidationLevel(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationResult:
    """Result of a validation check"""

    def __init__(self, level: ValidationLevel, key: str, message: str):
        self.level = level
        self.key = key
        self.message = message

    def __str__(self) -> str:
        icon = "❌" if self.level == ValidationLevel.ERROR else "⚠️" if self.level == ValidationLevel.WARNING else "ℹ️"
        return f"{icon} {self.message}"

    def __repr__(self) -> str:
        return f"ValidationResult({self.level.value}, {self.key}, {self.message})"


class ConfigValidator:
    """Validate SAP configuration against schema"""

    def __init__(self, schema: Optional[ConfigSchema] = None, schema_path: Optional[Path] = None):
        """
        Initialize validator
        
        Args:
            schema: ConfigSchema instance (optional)
            schema_path: Path to schema YAML file (optional)
        """
        if schema:
            self.schema = schema
        else:
            self.schema = ConfigSchema(schema_path)

    def validate(self, config_path: Path, environment: str = "dev", 
                 fail_on_warning: bool = False) -> Tuple[List[ValidationResult], bool]:
        """
        Validate configuration file or directory
        
        Args:
            config_path: Path to config file or directory
            environment: Environment name (dev, qa, prod)
            fail_on_warning: If True, warnings are treated as errors
            
        Returns:
            Tuple of (validation_results, is_valid)
        """
        # Load configuration
        try:
            config = ConfigLoader.load_from_path(config_path)
        except Exception as e:
            return [ValidationResult(
                ValidationLevel.ERROR,
                "config_load",
                f"Failed to load configuration: {str(e)}"
            )], False

        results = []
        
        # Check required keys
        results.extend(self._check_required_keys(config))
        
        # Check patterns
        results.extend(self._check_patterns(config))
        
        # Check secure keys (warnings if missing)
        results.extend(self._check_secure_keys(config))
        
        # Check minimum lengths
        results.extend(self._check_min_lengths(config))
        
        # Environment-specific checks
        if environment.lower() == "prod":
            results.extend(self._check_production_rules(config))
        
        # Determine if valid
        has_errors = any(r.level == ValidationLevel.ERROR for r in results)
        has_warnings = any(r.level == ValidationLevel.WARNING for r in results)
        
        is_valid = not has_errors and (not fail_on_warning or not has_warnings)
        
        return results, is_valid

    def _check_required_keys(self, config: Dict[str, str]) -> List[ValidationResult]:
        """Check for missing required keys"""
        results = []
        required = self.schema.get_required_keys()
        
        for key in required:
            if key not in config or not config[key]:
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    key,
                    f"Missing required key: {key}"
                ))
        
        return results

    def _check_patterns(self, config: Dict[str, str]) -> List[ValidationResult]:
        """Check values against regex patterns"""
        results = []
        patterns = self.schema.get_patterns()
        
        for key, pattern in patterns.items():
            if key in config:
                value = config[key]
                if not self.schema.validate_pattern(key, value):
                    results.append(ValidationResult(
                        ValidationLevel.ERROR,
                        key,
                        f"Invalid pattern: {key} = {value} (expected pattern: {pattern})"
                    ))
        
        return results

    def _check_secure_keys(self, config: Dict[str, str]) -> List[ValidationResult]:
        """Check secure keys (warn if missing or empty)"""
        results = []
        secure_keys = self.schema.get_secure_keys()
        
        for key in secure_keys:
            if key not in config or not config[key]:
                results.append(ValidationResult(
                    ValidationLevel.WARNING,
                    key,
                    f"Secure key missing or empty: {key}"
                ))
            elif len(config[key]) < 4:  # Suspiciously short
                results.append(ValidationResult(
                    ValidationLevel.WARNING,
                    key,
                    f"Secure key seems too short: {key}"
                ))
        
        return results

    def _check_min_lengths(self, config: Dict[str, str]) -> List[ValidationResult]:
        """Check minimum length requirements"""
        results = []
        min_lengths = self.schema.get_min_lengths()
        
        for key, min_length in min_lengths.items():
            if key in config and len(config[key]) < min_length:
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    key,
                    f"Value too short: {key} must be at least {min_length} characters"
                ))
        
        return results

    def _check_production_rules(self, config: Dict[str, str]) -> List[ValidationResult]:
        """Check production-specific rules"""
        results = []
        forbidden = self.schema.get_forbidden_in_prod()
        
        for key, value in config.items():
            if self.schema.is_forbidden_in_prod(value):
                results.append(ValidationResult(
                    ValidationLevel.ERROR,
                    key,
                    f"Production violation: {key} contains forbidden value (found in: {value})"
                ))
        
        return results


def validate(config_path: str, schema_path: Optional[str] = None, 
             environment: str = "dev", fail_on_warning: bool = False) -> Tuple[List[ValidationResult], bool]:
    """
    Convenience function to validate configuration
    
    Args:
        config_path: Path to config file or directory
        schema_path: Optional path to schema YAML file
        environment: Environment name (dev, qa, prod)
        fail_on_warning: If True, warnings are treated as errors
        
    Returns:
        Tuple of (validation_results, is_valid)
    """
    config_path_obj = Path(config_path)
    schema_path_obj = Path(schema_path) if schema_path else None
    
    validator = ConfigValidator(schema_path=schema_path_obj)
    return validator.validate(config_path_obj, environment, fail_on_warning)

