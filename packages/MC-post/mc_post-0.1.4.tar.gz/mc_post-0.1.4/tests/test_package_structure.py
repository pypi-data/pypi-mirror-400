"""
Property-based tests for package structure integrity.

**Feature: mcpost-package-improvement, Property 1: Package Structure Integrity**
**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4**
"""

import pytest
from pathlib import Path
import importlib
import sys
from hypothesis import given, strategies as st, settings, HealthCheck
import ast
import os


class TestPackageStructureIntegrity:
    """Test package structure integrity properties."""

    def test_package_structure_integrity_property(self, package_root):
        """
        Property 1: Package Structure Integrity
        
        For any valid MCPost installation, the package directory structure should 
        contain all required files and modules in their expected locations with 
        proper Python package hierarchy.
        
        **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4**
        """
        # Test core package structure exists
        mcpost_dir = package_root / "mcpost"
        assert mcpost_dir.exists(), "Main mcpost package directory must exist"
        assert mcpost_dir.is_dir(), "mcpost must be a directory"
        
        # Test required package files exist (Requirement 1.1, 1.4)
        required_files = [
            "mcpost/__init__.py",
            "mcpost/_version.py", 
            "mcpost/py.typed",
        ]
        
        for file_path in required_files:
            full_path = package_root / file_path
            assert full_path.exists(), f"Required file {file_path} must exist"
            assert full_path.is_file(), f"{file_path} must be a file"
        
        # Test module hierarchy exists (Requirement 1.3, 2.1, 2.2, 2.3, 2.4)
        required_modules = [
            "mcpost/gsa/__init__.py",
            "mcpost/gsa/pipeline.py",
            "mcpost/gsa/metrics.py", 
            "mcpost/gsa/kernels.py",
            "mcpost/gsa/plotting.py",
            "mcpost/integration/__init__.py",
            "mcpost/integration/monte_carlo.py",
            "mcpost/integration/quasi_monte_carlo.py",
            "mcpost/integration/importance.py",
            "mcpost/utils/__init__.py",
            "mcpost/utils/data.py",
            "mcpost/utils/validation.py",
            "mcpost/utils/config.py",
        ]
        
        for module_path in required_modules:
            full_path = package_root / module_path
            assert full_path.exists(), f"Required module {module_path} must exist"
            assert full_path.is_file(), f"{module_path} must be a file"
        
        # Test distribution files exist (Requirement 1.5)
        distribution_files = [
            "README.md",
            "LICENSE", 
            "MANIFEST.in",
            "CHANGELOG.md",
            "pyproject.toml",
        ]
        
        for dist_file in distribution_files:
            full_path = package_root / dist_file
            assert full_path.exists(), f"Distribution file {dist_file} must exist"
            assert full_path.is_file(), f"{dist_file} must be a file"
    
    def test_init_files_are_valid_python(self, package_root):
        """
        Test that all __init__.py files contain valid Python code and proper exports.
        
        **Validates: Requirements 1.4, 2.1**
        """
        init_files = [
            "mcpost/__init__.py",
            "mcpost/gsa/__init__.py", 
            "mcpost/integration/__init__.py",
            "mcpost/utils/__init__.py",
        ]
        
        for init_file in init_files:
            full_path = package_root / init_file
            
            # Test file is valid Python
            with open(full_path, 'r') as f:
                content = f.read()
            
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"Invalid Python syntax in {init_file}: {e}")
            
            # Test __all__ is defined for public API (Requirement 1.4)
            tree = ast.parse(content)
            has_all = any(
                isinstance(node, ast.Assign) and 
                any(isinstance(target, ast.Name) and target.id == '__all__' 
                    for target in node.targets)
                for node in tree.body
            )
            assert has_all, f"{init_file} must define __all__ for public API"
    
    def test_pyproject_toml_structure(self, package_root):
        """
        Test that pyproject.toml has proper structure for modern packaging.
        
        **Validates: Requirements 1.2**
        """
        pyproject_path = package_root / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml must exist"
        
        # Read and parse TOML content
        try:
            import tomllib
        except ImportError:
            # Python < 3.11 fallback
            try:
                import tomli as tomllib
            except ImportError:
                pytest.skip("TOML parsing library not available")
        
        with open(pyproject_path, 'rb') as f:
            config = tomllib.load(f)
        
        # Test required sections exist
        required_sections = ["build-system", "project"]
        for section in required_sections:
            assert section in config, f"pyproject.toml must have [{section}] section"
        
        # Test project metadata
        project = config["project"]
        required_fields = ["name", "description", "dependencies"]
        for field in required_fields:
            assert field in project, f"project section must have {field} field"
        
        # Check version is either static or dynamic
        has_static_version = "version" in project
        has_dynamic_version = "dynamic" in project and "version" in project["dynamic"]
        assert has_static_version or has_dynamic_version, "project section must have version field (static or dynamic)"
        
        assert project["name"] == "mcpost", "Package name must be 'mcpost'"
        assert isinstance(project["dependencies"], list), "Dependencies must be a list"
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    @settings(max_examples=2, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_module_imports_work(self, package_root, module_name):
        """
        Property test: For any valid module name in the package structure,
        importing should work without errors.
        
        **Validates: Requirements 1.3, 2.1**
        """
        # Only test actual modules that exist
        valid_modules = [
            "mcpost",
            "mcpost.gsa", 
            "mcpost.integration",
            "mcpost.utils",
        ]
        
        # Add package root to Python path temporarily
        original_path = sys.path.copy()
        try:
            if str(package_root) not in sys.path:
                sys.path.insert(0, str(package_root))
            
            for module in valid_modules:
                try:
                    importlib.import_module(module)
                except ImportError as e:
                    # Allow NotImplementedError for placeholder functions
                    if "NotImplementedError" not in str(e):
                        pytest.fail(f"Failed to import {module}: {e}")
        finally:
            sys.path = original_path
    
    def test_package_metadata_consistency(self, package_root):
        """
        Test that package metadata is consistent across files.
        
        **Validates: Requirements 1.2, 1.5**
        """
        # Read version from _version.py
        version_file = package_root / "mcpost" / "_version.py"
        with open(version_file, 'r') as f:
            version_content = f.read()
        
        # Extract version using AST
        tree = ast.parse(version_content)
        version = None
        for node in tree.body:
            if (isinstance(node, ast.Assign) and 
                len(node.targets) == 1 and
                isinstance(node.targets[0], ast.Name) and
                node.targets[0].id == '__version__'):
                if isinstance(node.value, ast.Constant):
                    version = node.value.value
                    break
        
        assert version is not None, "_version.py must define __version__"
        assert isinstance(version, str), "Version must be a string"
        assert len(version.split('.')) >= 2, "Version must follow semantic versioning"
        
        # Check pyproject.toml version configuration
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                pytest.skip("TOML parsing library not available")
        
        pyproject_path = package_root / "pyproject.toml"
        with open(pyproject_path, 'rb') as f:
            config = tomllib.load(f)
        
        project = config["project"]
        
        # Check if version is static or dynamic
        if "version" in project:
            # Static version - should match _version.py
            pyproject_version = project["version"]
            assert version == pyproject_version, "Version must be consistent between _version.py and pyproject.toml"
        elif "dynamic" in project and "version" in project["dynamic"]:
            # Dynamic version - check that setuptools configuration exists
            assert "tool" in config, "Dynamic versioning requires tool configuration"
            assert "setuptools" in config["tool"], "Dynamic versioning requires setuptools configuration"
            assert "dynamic" in config["tool"]["setuptools"], "Dynamic versioning requires setuptools.dynamic configuration"
            setuptools_dynamic = config["tool"]["setuptools"]["dynamic"]
            assert "version" in setuptools_dynamic, "Dynamic version must be configured in tool.setuptools.dynamic"
            
            # Check that the version attribute path is correct
            version_config = setuptools_dynamic["version"]
            if isinstance(version_config, dict) and "attr" in version_config:
                expected_attr = "mcpost._version.__version__"
                assert version_config["attr"] == expected_attr, f"Version attribute should be {expected_attr}"
        else:
            pytest.fail("Project must have either static version or dynamic version configuration")