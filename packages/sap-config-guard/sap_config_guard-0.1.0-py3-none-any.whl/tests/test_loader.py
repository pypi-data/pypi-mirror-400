"""
Tests for configuration loader
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from sap_config_guard.core.loader import ConfigLoader


def test_load_env_file():
    """Test loading .env file"""
    with TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_file.write_text(
            "SAP_CLIENT=100\n"
            "SAP_SYSTEM_ID=ABC\n"
            "# This is a comment\n"
            "SAP_API_URL=https://api.sap.com\n"
        )
        
        config = ConfigLoader.load_from_path(env_file)
        
        assert config["SAP_CLIENT"] == "100"
        assert config["SAP_SYSTEM_ID"] == "ABC"
        assert config["SAP_API_URL"] == "https://api.sap.com"
        assert "#" not in config


def test_load_properties_file():
    """Test loading .properties file"""
    with TemporaryDirectory() as tmpdir:
        props_file = Path(tmpdir) / "config.properties"
        props_file.write_text(
            "SAP_CLIENT=100\n"
            "SAP_SYSTEM_ID=ABC\n"
            "# Comment\n"
            "SAP_API_URL=https://api.sap.com\n"
        )
        
        config = ConfigLoader.load_from_path(props_file)
        
        assert config["SAP_CLIENT"] == "100"
        assert config["SAP_SYSTEM_ID"] == "ABC"
        assert config["SAP_API_URL"] == "https://api.sap.com"


def test_load_json_file():
    """Test loading JSON file"""
    import json
    
    with TemporaryDirectory() as tmpdir:
        json_file = Path(tmpdir) / "config.json"
        json_data = {
            "SAP_CLIENT": "100",
            "SAP_SYSTEM_ID": "ABC",
            "SAP_API_URL": "https://api.sap.com"
        }
        json_file.write_text(json.dumps(json_data))
        
        config = ConfigLoader.load_from_path(json_file)
        
        assert config["SAP_CLIENT"] == "100"
        assert config["SAP_SYSTEM_ID"] == "ABC"
        assert config["SAP_API_URL"] == "https://api.sap.com"


def test_load_yaml_file():
    """Test loading YAML file"""
    import yaml
    
    with TemporaryDirectory() as tmpdir:
        yaml_file = Path(tmpdir) / "config.yaml"
        yaml_data = {
            "SAP_CLIENT": "100",
            "SAP_SYSTEM_ID": "ABC",
            "SAP_API_URL": "https://api.sap.com"
        }
        yaml_file.write_text(yaml.dump(yaml_data))
        
        config = ConfigLoader.load_from_path(yaml_file)
        
        assert config["SAP_CLIENT"] == "100"
        assert config["SAP_SYSTEM_ID"] == "ABC"
        assert config["SAP_API_URL"] == "https://api.sap.com"


def test_load_directory():
    """Test loading from directory"""
    with TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_file.write_text("SAP_CLIENT=100\n")
        
        props_file = Path(tmpdir) / "config.properties"
        props_file.write_text("SAP_API_URL=https://api.sap.com\n")
        
        config = ConfigLoader.load_from_path(Path(tmpdir))
        
        assert "SAP_CLIENT" in config
        assert "SAP_API_URL" in config

