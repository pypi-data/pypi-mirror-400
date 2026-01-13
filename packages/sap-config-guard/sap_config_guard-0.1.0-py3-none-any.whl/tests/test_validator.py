"""
Tests for configuration validator
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
import os

from sap_config_guard.core.validator import ConfigValidator, ValidationLevel
from sap_config_guard.core.schema import ConfigSchema
from sap_config_guard.core.loader import ConfigLoader


def test_required_keys_validation():
    """Test validation of required keys"""
    schema = ConfigSchema()
    validator = ConfigValidator(schema=schema)
    
    with TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.env"
        config_file.write_text("SAP_CLIENT=100\nSAP_SYSTEM_ID=ABC")
        # Missing SAP_API_URL
        
        results, is_valid = validator.validate(Path(tmpdir), environment="dev")
        
        assert not is_valid
        assert any("SAP_API_URL" in str(r) for r in results)


def test_pattern_validation():
    """Test pattern validation"""
    schema = ConfigSchema()
    validator = ConfigValidator(schema=schema)
    
    with TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.env"
        config_file.write_text("SAP_CLIENT=12\nSAP_SYSTEM_ID=ABC\nSAP_API_URL=https://api.sap.com")
        # SAP_CLIENT should be 3 digits
        
        results, is_valid = validator.validate(Path(tmpdir), environment="dev")
        
        assert not is_valid
        assert any("SAP_CLIENT" in str(r) and "pattern" in str(r).lower() for r in results)


def test_production_rules():
    """Test production-specific validation rules"""
    schema = ConfigSchema()
    validator = ConfigValidator(schema=schema)
    
    with TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.env"
        config_file.write_text("SAP_CLIENT=100\nSAP_SYSTEM_ID=ABC\nSAP_API_URL=http://localhost:8080")
        # localhost is forbidden in prod
        
        results, is_valid = validator.validate(Path(tmpdir), environment="prod")
        
        assert not is_valid
        assert any("localhost" in str(r).lower() or "forbidden" in str(r).lower() for r in results)


def test_valid_config():
    """Test that valid configuration passes"""
    schema = ConfigSchema()
    validator = ConfigValidator(schema=schema)
    
    with TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.env"
        config_file.write_text(
            "SAP_CLIENT=100\n"
            "SAP_SYSTEM_ID=ABC\n"
            "SAP_API_URL=https://api.sap.com\n"
            "SAP_PASSWORD=securepass123"
        )
        
        results, is_valid = validator.validate(Path(tmpdir), environment="dev")
        
        # Should be valid (warnings for secure keys are OK in dev)
        assert is_valid or all(r.level == ValidationLevel.WARNING for r in results)


def test_min_length_validation():
    """Test minimum length validation"""
    schema = ConfigSchema()
    validator = ConfigValidator(schema=schema)
    
    with TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.env"
        config_file.write_text(
            "SAP_CLIENT=100\n"
            "SAP_SYSTEM_ID=ABC\n"
            "SAP_API_URL=https://api.sap.com\n"
            "SAP_PASSWORD=short"  # Less than 8 characters
        )
        
        results, is_valid = validator.validate(Path(tmpdir), environment="dev")
        
        assert not is_valid
        assert any("too short" in str(r).lower() or "8" in str(r) for r in results)

