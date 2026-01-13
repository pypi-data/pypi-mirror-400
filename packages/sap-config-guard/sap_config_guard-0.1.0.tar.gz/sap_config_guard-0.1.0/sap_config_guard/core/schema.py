"""
Schema definitions and validation rules for SAP configurations
"""

import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml


class ConfigSchema:
    """Schema definition for SAP configuration validation"""

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize schema from file or use defaults
        
        Args:
            schema_path: Path to YAML schema file
        """
        if schema_path and schema_path.exists():
            with open(schema_path, 'r') as f:
                self.schema = yaml.safe_load(f)
        else:
            self.schema = self._default_schema()

    def _default_schema(self) -> Dict[str, Any]:
        """Default SAP configuration schema"""
        return {
            'required': [
                'SAP_CLIENT',
                'SAP_SYSTEM_ID',
                'SAP_API_URL'
            ],
            'secure': [
                'SAP_PASSWORD',
                'SAP_PRIVATE_KEY',
                'SAP_SECRET',
                'SAP_OAUTH_SECRET'
            ],
            'patterns': {
                'SAP_CLIENT': r'^[0-9]{3}$',
                'SAP_API_URL': r'^https://.*',
                'SAP_SYSTEM_ID': r'^[A-Z0-9]{3}$'
            },
            'forbidden_in_prod': [
                'mock',
                'localhost',
                '127.0.0.1',
                'test',
                'dev'
            ],
            'min_lengths': {
                'SAP_PASSWORD': 8
            },
            'allowed_values': {}
        }

    def get_required_keys(self) -> List[str]:
        """Get list of required configuration keys"""
        return self.schema.get('required', [])

    def get_secure_keys(self) -> List[str]:
        """Get list of secure/secret keys"""
        return self.schema.get('secure', [])

    def get_patterns(self) -> Dict[str, str]:
        """Get regex patterns for key validation"""
        return self.schema.get('patterns', {})

    def get_forbidden_in_prod(self) -> List[str]:
        """Get list of forbidden values in production"""
        return self.schema.get('forbidden_in_prod', [])

    def get_min_lengths(self) -> Dict[str, int]:
        """Get minimum length requirements"""
        return self.schema.get('min_lengths', {})

    def validate_pattern(self, key: str, value: str) -> bool:
        """
        Validate value against pattern for key
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Returns:
            True if pattern matches
        """
        patterns = self.get_patterns()
        if key not in patterns:
            return True  # No pattern defined
        
        pattern = patterns[key]
        return bool(re.match(pattern, str(value)))

    def is_forbidden_in_prod(self, value: str) -> bool:
        """
        Check if value is forbidden in production
        
        Args:
            value: Configuration value to check
            
        Returns:
            True if value contains forbidden strings
        """
        value_lower = str(value).lower()
        forbidden = self.get_forbidden_in_prod()
        return any(forbidden_item in value_lower for forbidden_item in forbidden)

