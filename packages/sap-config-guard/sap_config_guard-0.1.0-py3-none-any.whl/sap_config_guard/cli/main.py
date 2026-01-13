"""
CLI entry point for sap-config-guard
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from sap_config_guard.core.validator import ConfigValidator, ValidationLevel
from sap_config_guard.core.schema import ConfigSchema
from sap_config_guard.diff.env_diff import EnvironmentDiff, DiffResult


def validate_command(args):
    """Execute validate command"""
    config_path = Path(args.config_path)
    
    if not config_path.exists():
        print(f"❌ Error: Config path not found: {config_path}")
        sys.exit(1)
    
    schema_path = Path(args.schema) if args.schema else None
    validator = ConfigValidator(schema_path=schema_path)
    
    results, is_valid = validator.validate(
        config_path=config_path,
        environment=args.environment,
        fail_on_warning=args.fail_on_warning
    )
    
    # Print results
    if results:
        for result in results:
            print(result)
    else:
        print("✅ Configuration is valid!")
    
    # Exit with appropriate code
    if not is_valid:
        sys.exit(1)
    else:
        sys.exit(0)


def diff_command(args):
    """Execute diff command"""
    env_paths = {}
    
    # Parse environment paths
    for env_arg in args.environments:
        if '=' in env_arg:
            env_name, env_path = env_arg.split('=', 1)
            env_paths[env_name] = Path(env_path)
        else:
            # Assume format: env_name:path
            if ':' in env_arg:
                env_name, env_path = env_arg.split(':', 1)
                env_paths[env_name] = Path(env_path)
            else:
                # Last resort: use as path, infer name from path
                env_path = Path(env_arg)
                env_name = env_path.name
                env_paths[env_name] = env_path
    
    # If only paths provided without names, use positional args
    if len(args.environments) == len(env_paths) and all('=' not in arg and ':' not in arg for arg in args.environments):
        # Assume they're in order: dev, qa, prod
        env_names = ['dev', 'qa', 'prod'][:len(args.environments)]
        env_paths = {name: Path(path) for name, path in zip(env_names, args.environments)}
    
    # Validate paths exist
    for env_name, env_path in env_paths.items():
        if not env_path.exists():
            print(f"❌ Error: Environment path not found: {env_name} -> {env_path}")
            sys.exit(1)
    
    # Compare environments
    results = EnvironmentDiff.compare_environments(env_paths)
    
    # Format and print
    output = EnvironmentDiff.format_diff_results(results, show_same=args.show_same)
    print(output)
    
    # Exit with error if drift detected
    if results and any(r.status in ['missing', 'different'] for r in results):
        if args.fail_on_drift:
            sys.exit(1)
    else:
        sys.exit(0)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="sap-config-guard: Fail-fast configuration validation & environment drift detection for SAP landscapes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a configuration
  sap-config-guard validate ./config/dev

  # Validate with custom schema
  sap-config-guard validate ./config/prod --schema ./schema.yaml

  # Validate production with strict mode
  sap-config-guard validate ./config/prod --environment prod --fail-on-warning

  # Compare environments
  sap-config-guard diff dev=./config/dev qa=./config/qa prod=./config/prod

  # Compare environments (positional)
  sap-config-guard diff ./config/dev ./config/qa ./config/prod
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')
    validate_parser.add_argument('config_path', help='Path to config file or directory')
    validate_parser.add_argument('--schema', '-s', help='Path to schema YAML file')
    validate_parser.add_argument('--environment', '-e', default='dev', 
                                choices=['dev', 'qa', 'prod'],
                                help='Environment name (default: dev)')
    validate_parser.add_argument('--fail-on-warning', action='store_true',
                                help='Treat warnings as errors')
    validate_parser.set_defaults(func=validate_command)
    
    # Diff command
    diff_parser = subparsers.add_parser('diff', help='Compare configurations across environments')
    diff_parser.add_argument('environments', nargs='+',
                            help='Environment paths (format: name=path or just path)')
    diff_parser.add_argument('--show-same', action='store_true',
                            help='Show keys that are the same across environments')
    diff_parser.add_argument('--fail-on-drift', action='store_true',
                            help='Exit with error code if drift is detected')
    diff_parser.set_defaults(func=diff_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()

