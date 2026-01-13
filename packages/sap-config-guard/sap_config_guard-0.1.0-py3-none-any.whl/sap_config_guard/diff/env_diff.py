"""
Environment diff and drift detection
"""

from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

from sap_config_guard.core.loader import ConfigLoader


@dataclass
class DiffResult:
    """Result of environment comparison"""
    key: str
    environments: Dict[str, str]
    status: str  # 'missing', 'different', 'same'
    message: str


class EnvironmentDiff:
    """Compare configurations across environments"""

    @staticmethod
    def compare_environments(env_paths: Dict[str, Path]) -> List[DiffResult]:
        """
        Compare configurations across multiple environments
        
        Args:
            env_paths: Dictionary mapping environment names to config paths
                      e.g., {'dev': Path('./config/dev'), 'qa': Path('./config/qa')}
        
        Returns:
            List of DiffResult objects
        """
        # Load all environment configs
        env_configs = {}
        for env_name, env_path in env_paths.items():
            try:
                env_configs[env_name] = ConfigLoader.load_from_path(env_path)
            except Exception as e:
                env_configs[env_name] = {}
                print(f"Warning: Failed to load {env_name} config: {e}")
        
        # Get all unique keys across environments
        all_keys: Set[str] = set()
        for config in env_configs.values():
            all_keys.update(config.keys())
        
        results = []
        
        # Compare each key across environments
        for key in sorted(all_keys):
            key_values = {}
            present_in = []
            
            for env_name, config in env_configs.items():
                if key in config:
                    key_values[env_name] = config[key]
                    present_in.append(env_name)
            
            # Check if key is missing in some environments
            if len(present_in) < len(env_paths):
                missing_in = set(env_paths.keys()) - set(present_in)
                results.append(DiffResult(
                    key=key,
                    environments=key_values,
                    status='missing',
                    message=f"Key '{key}' missing in: {', '.join(missing_in)}"
                ))
            # Check if values differ
            elif len(set(key_values.values())) > 1:
                value_str = ', '.join(f"{env}={val}" for env, val in key_values.items())
                results.append(DiffResult(
                    key=key,
                    environments=key_values,
                    status='different',
                    message=f"Key '{key}' differs: {value_str}"
                ))
            # Values are the same (optional - can be filtered)
            # else:
            #     results.append(DiffResult(
            #         key=key,
            #         environments=key_values,
            #         status='same',
            #         message=f"Key '{key}' is consistent across environments"
            #     ))
        
        return results

    @staticmethod
    def format_diff_results(results: List[DiffResult], show_same: bool = False) -> str:
        """
        Format diff results for display
        
        Args:
            results: List of DiffResult objects
            show_same: Whether to show keys that are the same across environments
        
        Returns:
            Formatted string
        """
        if not results:
            return "✅ No differences detected"
        
        output = []
        output.append("⚠️  Drift detected:\n")
        
        for result in results:
            if result.status == 'same' and not show_same:
                continue
            
            if result.status == 'missing':
                output.append(f"  ❌ {result.message}")
            elif result.status == 'different':
                output.append(f"  ⚠️  {result.message}")
            elif result.status == 'same':
                output.append(f"  ✅ {result.message}")
        
        return "\n".join(output)


def compare_environments(env_paths: Dict[str, str]) -> List[DiffResult]:
    """
    Convenience function to compare environments
    
    Args:
        env_paths: Dictionary mapping environment names to config paths (strings)
    
    Returns:
        List of DiffResult objects
    """
    env_paths_obj = {env: Path(path) for env, path in env_paths.items()}
    return EnvironmentDiff.compare_environments(env_paths_obj)

