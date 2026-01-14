"""
Test that the package works correctly without excluded code/directories.

This test verifies that:
1. The package can be built successfully
2. Excluded directories are not included in the built package
3. Core functionality works without the excluded code
"""

import subprocess
import tempfile
import zipfile
from pathlib import Path



def test_package_build_excludes_private_code():
    """Test that building the package excludes private directories."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    
    # Create a temporary directory for the build
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Build the package
        result = subprocess.run(
            ["uv", "build", "--out-dir", str(temp_path)],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        # Verify build succeeded
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        
        # Find the wheel file
        wheel_files = list(temp_path.glob("*.whl"))
        assert len(wheel_files) == 1, f"Expected 1 wheel file, found {len(wheel_files)}"
        wheel_path = wheel_files[0]
        
        # Check wheel contents
        with zipfile.ZipFile(wheel_path) as wheel:
            contents = wheel.namelist()
            
            # Verify excluded directories are not present
            excluded_patterns = [
                "hwo_disra/disra_notebooks/",
                "hwo_disra/yields/lowzmassivestars/",
                "notebooks/"
            ]
            
            for pattern in excluded_patterns:
                matching_files = [f for f in contents if pattern in f]
                assert not matching_files, f"Found excluded files with pattern '{pattern}': {matching_files}"
            
            # Verify only the API test notebook is included
            ipynb_files = [f for f in contents if f.endswith('.ipynb')]
            assert len(ipynb_files) == 2, f"Expected 2 notebook files, found {len(ipynb_files)}: {ipynb_files}"
            assert "hwo_disra/tests/resources/hwo_disra-api-test.ipynb" in ipynb_files[0]
            
            # Verify core modules are included
            required_modules = [
                "hwo_disra/__init__.py",
                "hwo_disra/DRMinator.py",
                "hwo_disra/Yieldinator.py",
                "hwo_disra/yields/BDYieldinator.py",
                "hwo_disra/yields/KBOYieldinator.py",
                "hwo_disra/yields/QSOYieldinator.py",
                "hwo_disra/yields/StellarEvolution.py"
            ]
            
            for module in required_modules:
                assert any(module in f for f in contents), f"Required module '{module}' not found in package"


def test_excluded_modules_not_in_package():
    """Test that excluded modules are not accessible in the built package."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    
    # Create a temporary directory for the build
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Build the package
        result = subprocess.run(
            ["uv", "build", "--out-dir", str(temp_path)],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        # Verify build succeeded
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        
        # Find the wheel file
        wheel_files = list(temp_path.glob("*.whl"))
        assert len(wheel_files) == 1, f"Expected 1 wheel file, found {len(wheel_files)}"
        wheel_path = wheel_files[0]
        
        # Check that specific excluded modules are not in the wheel
        with zipfile.ZipFile(wheel_path) as wheel:
            contents = wheel.namelist()
            
            # Verify that lowzmassivestars directory is completely absent from yields and package
            lowz_files = [f for f in contents if "lowzmassivestars" in f]
            assert not lowz_files, f"Found lowzmassivestars files in package: {lowz_files}"
            
            # Verify disra_notebooks directory is completely absent  
            disra_files = [f for f in contents if "disra_notebooks" in f]
            assert not disra_files, f"Found disra_notebooks files in package: {disra_files}"


def test_package_structure_integrity():
    """Test that the package has the expected structure without excluded components."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Build the package
        result = subprocess.run(
            ["uv", "build", "--out-dir", str(temp_path)],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        
        # Find the wheel file
        wheel_files = list(temp_path.glob("*.whl"))
        wheel_path = wheel_files[0]
        
        with zipfile.ZipFile(wheel_path) as wheel:
            contents = wheel.namelist()
            
            # Check that core yields modules are present
            expected_yield_modules = [
                "hwo_disra/yields/__init__.py",
                "hwo_disra/yields/BDYieldinator.py", 
                "hwo_disra/yields/KBOYieldinator.py",
                "hwo_disra/yields/QSOYieldinator.py",
                "hwo_disra/yields/StellarEvolution.py"
            ]
            
            for module in expected_yield_modules:
                assert any(module in f for f in contents), f"Expected module '{module}' not found in package"
            
            # Check that exactly one test notebook is present
            test_notebooks = [f for f in contents if f.endswith('.ipynb')]
            assert len(test_notebooks) == 2, f"Expected exactly 2 test notebooks, found {len(test_notebooks)}: {test_notebooks}"
            assert "hwo_disra/tests/resources/hwo_disra-api-test.ipynb" in test_notebooks[0]
            
            # Verify complete notebooks are excluded
            complete_notebook_patterns = [
                "KBO_survey_hwo_disra.ipynb",
                "DISRA_SCDD-rise-of-oxygen.ipynb", 
                "lowzmassivestars-hwo_disra-notebook.ipynb"
            ]
            
            for pattern in complete_notebook_patterns:
                notebook_files = [f for f in contents if pattern in f]
                assert not notebook_files, f"Complete notebook '{pattern}' found in package: {notebook_files}"