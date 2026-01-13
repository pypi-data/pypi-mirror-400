"""
sap-config-guard: Fail-fast configuration validation & environment drift detection for SAP landscapes
"""

__version__ = "0.1.0"
__author__ = "SAP Community"

from sap_config_guard.core.validator import validate
from sap_config_guard.diff.env_diff import compare_environments

__all__ = ["validate", "compare_environments"]

