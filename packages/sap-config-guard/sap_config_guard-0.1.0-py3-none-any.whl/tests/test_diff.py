"""
Tests for environment diff
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from sap_config_guard.diff.env_diff import EnvironmentDiff, DiffResult


def test_compare_environments_same():
    """Test comparing environments with same config"""
    with TemporaryDirectory() as tmpdir:
        dev_dir = Path(tmpdir) / "dev"
        qa_dir = Path(tmpdir) / "qa"
        dev_dir.mkdir()
        qa_dir.mkdir()
        
        (dev_dir / ".env").write_text("SAP_CLIENT=100\nSAP_API_URL=https://api.sap.com\n")
        (qa_dir / ".env").write_text("SAP_CLIENT=100\nSAP_API_URL=https://api.sap.com\n")
        
        results = EnvironmentDiff.compare_environments({
            "dev": dev_dir,
            "qa": qa_dir
        })
        
        # Should have no differences
        assert all(r.status != "different" for r in results)


def test_compare_environments_different():
    """Test comparing environments with different config"""
    with TemporaryDirectory() as tmpdir:
        dev_dir = Path(tmpdir) / "dev"
        qa_dir = Path(tmpdir) / "qa"
        dev_dir.mkdir()
        qa_dir.mkdir()
        
        (dev_dir / ".env").write_text("SAP_CLIENT=100\nSAP_API_URL=http://localhost:8080\n")
        (qa_dir / ".env").write_text("SAP_CLIENT=100\nSAP_API_URL=https://qa.sap.com\n")
        
        results = EnvironmentDiff.compare_environments({
            "dev": dev_dir,
            "qa": qa_dir
        })
        
        # Should detect difference in SAP_API_URL
        assert any(r.key == "SAP_API_URL" and r.status == "different" for r in results)


def test_compare_environments_missing():
    """Test comparing environments with missing keys"""
    with TemporaryDirectory() as tmpdir:
        dev_dir = Path(tmpdir) / "dev"
        qa_dir = Path(tmpdir) / "qa"
        dev_dir.mkdir()
        qa_dir.mkdir()
        
        (dev_dir / ".env").write_text("SAP_CLIENT=100\nSAP_API_URL=https://api.sap.com\n")
        (qa_dir / ".env").write_text("SAP_CLIENT=100\n")  # Missing SAP_API_URL
        
        results = EnvironmentDiff.compare_environments({
            "dev": dev_dir,
            "qa": qa_dir
        })
        
        # Should detect missing key
        assert any(r.key == "SAP_API_URL" and r.status == "missing" for r in results)

