"""Tests for the CLI."""

import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from product_kit.cli import app

runner = CliRunner()


def test_help():
    """Test help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "prod" in result.stdout


def test_no_prompts_mode():
    """Test non-interactive mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test-project"
        
        result = runner.invoke(
            app,
            [str(project_path), "--no-prompts"],
        )
        
        assert result.exit_code == 0
        assert project_path.exists()
        assert (project_path / "constitution.md").exists()
        assert (project_path / "context" / "product-vision.md").exists()
        assert (project_path / "templates" / "prd_template.md").exists()


def test_creates_directory_structure():
    """Test that all expected directories are created."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test-project"
        
        result = runner.invoke(
            app,
            [str(project_path), "--no-prompts"],
        )
        
        assert result.exit_code == 0
        
        # Check directories
        assert (project_path / "context").exists()
        assert (project_path / "inventory").exists()
        assert (project_path / "templates").exists()
        assert (project_path / ".github" / "agents").exists()


def test_replacements_applied():
    """Test that placeholder replacements work."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test-project"
        
        result = runner.invoke(
            app,
            [
                str(project_path),
                "--product-name", "Test Product",
                "--no-prompts",
            ],
        )
        
        assert result.exit_code == 0
        
        # Check that product name was replaced
        constitution = (project_path / "constitution.md").read_text()
        assert "Test Product" in constitution
