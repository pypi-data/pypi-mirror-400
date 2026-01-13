"""
Configuration file loader supporting multiple formats
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Optional, Any


class ConfigLoader:
    """Load configuration from various file formats"""

    @staticmethod
    def load_from_path(config_path: Path) -> Dict[str, str]:
        """
        Load configuration from a file or directory
        
        Args:
            config_path: Path to config file or directory
            
        Returns:
            Dictionary of key-value pairs
        """
        if config_path.is_file():
            return ConfigLoader._load_file(config_path)
        elif config_path.is_dir():
            return ConfigLoader._load_directory(config_path)
        else:
            raise FileNotFoundError(f"Config path not found: {config_path}")

    @staticmethod
    def _load_file(file_path: Path) -> Dict[str, str]:
        """Load configuration from a single file"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.json':
            return ConfigLoader._load_json(file_path)
        elif suffix in ['.yaml', '.yml']:
            return ConfigLoader._load_yaml(file_path)
        elif suffix == '.properties':
            return ConfigLoader._load_properties(file_path)
        elif suffix == '.env':
            return ConfigLoader._load_env(file_path)
        else:
            # Try as .env file
            return ConfigLoader._load_env(file_path)

    @staticmethod
    def _load_directory(dir_path: Path) -> Dict[str, str]:
        """Load configuration from directory (all .env, .properties, .yaml, .json files)"""
        config = {}
        
        # Common config file names
        config_files = [
            '.env',
            'config.env',
            'config.properties',
            'config.yaml',
            'config.yml',
            'config.json'
        ]
        
        for file_name in config_files:
            file_path = dir_path / file_name
            if file_path.exists():
                file_config = ConfigLoader._load_file(file_path)
                config.update(file_config)
        
        # Also load all .env files in directory
        for env_file in dir_path.glob('*.env'):
            if env_file.name not in ['.env', 'config.env']:
                file_config = ConfigLoader._load_file(env_file)
                config.update(file_config)
        
        return config

    @staticmethod
    def _load_json(file_path: Path) -> Dict[str, str]:
        """Load JSON configuration file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
            return ConfigLoader._flatten_dict(data)

    @staticmethod
    def _load_yaml(file_path: Path) -> Dict[str, str]:
        """Load YAML configuration file"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            return ConfigLoader._flatten_dict(data)

    @staticmethod
    def _load_properties(file_path: Path) -> Dict[str, str]:
        """Load Java properties file"""
        config = {}
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        return config

    @staticmethod
    def _load_env(file_path: Path) -> Dict[str, str]:
        """Load .env file"""
        config = {}
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    config[key.strip()] = value
        return config

    @staticmethod
    def _flatten_dict(data: Any, parent_key: str = '', sep: str = '_') -> Dict[str, str]:
        """
        Flatten nested dictionary to dot-notation keys
        
        Args:
            data: Dictionary or value to flatten
            parent_key: Parent key prefix
            sep: Separator for nested keys
            
        Returns:
            Flattened dictionary with string values
        """
        items = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}{sep}{key}" if parent_key else key
                if isinstance(value, dict):
                    items.extend(ConfigLoader._flatten_dict(value, new_key, sep=sep).items())
                elif isinstance(value, list):
                    # Convert lists to comma-separated strings
                    items.append((new_key, ','.join(str(v) for v in value)))
                else:
                    items.append((new_key, str(value)))
        else:
            items.append((parent_key, str(data)))
        
        return dict(items)

