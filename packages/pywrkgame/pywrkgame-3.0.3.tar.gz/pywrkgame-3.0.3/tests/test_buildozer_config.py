"""
Test Buildozer configuration for Android builds
Requirements: 2.8
"""

import pytest
import os
import configparser


class TestBuildozerConfiguration:
    """Test Buildozer configuration file"""
    
    def test_buildozer_spec_exists(self):
        """Test that buildozer.spec file exists"""
        assert os.path.exists("buildozer.spec"), "buildozer.spec file not found"
        
    def test_buildozer_spec_readable(self):
        """Test that buildozer.spec is readable"""
        config = configparser.ConfigParser()
        config.read("buildozer.spec")
        
        assert "app" in config.sections()
        assert "buildozer" in config.sections()
        
    def test_app_configuration(self):
        """Test app section configuration"""
        config = configparser.ConfigParser()
        config.read("buildozer.spec")
        
        # Check required app settings
        assert config.has_option("app", "title")
        assert config.has_option("app", "package.name")
        assert config.has_option("app", "package.domain")
        assert config.has_option("app", "version")
        
        # Verify values
        assert config.get("app", "title") == "PyWRKGame"
        assert config.get("app", "package.name") == "pywrkgame"
        assert config.get("app", "package.domain") == "org.pywrkgame"
        assert config.get("app", "version") == "3.0.0"
        
    def test_android_configuration(self):
        """Test Android-specific configuration"""
        config = configparser.ConfigParser()
        config.read("buildozer.spec")
        
        # Check Android API levels
        assert config.has_option("app", "android.api")
        assert config.has_option("app", "android.minapi")
        assert config.has_option("app", "android.ndk")
        
        # Verify API levels meet requirements (API 21+)
        min_api = int(config.get("app", "android.minapi"))
        assert min_api >= 21, "Minimum API should be 21 or higher (Android 5.0+)"
        
        target_api = int(config.get("app", "android.api"))
        assert target_api >= 21, "Target API should be 21 or higher"
        
    def test_android_permissions(self):
        """Test that required Android permissions are configured"""
        config = configparser.ConfigParser()
        config.read("buildozer.spec")
        
        assert config.has_option("app", "android.permissions")
        permissions = config.get("app", "android.permissions")
        
        # Check required permissions
        required_permissions = [
            "INTERNET",
            "ACCESS_NETWORK_STATE",
            "VIBRATE",
            "WRITE_EXTERNAL_STORAGE",
            "READ_EXTERNAL_STORAGE"
        ]
        
        for permission in required_permissions:
            assert permission in permissions, f"Missing required permission: {permission}"
            
    def test_android_architectures(self):
        """Test that Android architectures are configured"""
        config = configparser.ConfigParser()
        config.read("buildozer.spec")
        
        assert config.has_option("app", "android.archs")
        archs = config.get("app", "android.archs")
        
        # Should support at least arm64-v8a for modern devices
        assert "arm64-v8a" in archs, "Should support arm64-v8a architecture"
        
    def test_source_configuration(self):
        """Test source code configuration"""
        config = configparser.ConfigParser()
        config.read("buildozer.spec")
        
        # Check source directory
        assert config.has_option("app", "source.dir")
        
        # Check file extensions
        assert config.has_option("app", "source.include_exts")
        exts = config.get("app", "source.include_exts")
        
        # Should include Python and C++ files
        assert "py" in exts
        assert "cpp" in exts or "c" in exts
        assert "h" in exts
        
    def test_requirements_configured(self):
        """Test that Python requirements are configured"""
        config = configparser.ConfigParser()
        config.read("buildozer.spec")
        
        assert config.has_option("app", "requirements")
        requirements = config.get("app", "requirements")
        
        # Should include essential requirements
        assert "python3" in requirements
        assert "pybind11" in requirements
        
    def test_fullscreen_mode(self):
        """Test that fullscreen mode is configured for games"""
        config = configparser.ConfigParser()
        config.read("buildozer.spec")
        
        assert config.has_option("app", "fullscreen")
        fullscreen = config.get("app", "fullscreen")
        
        # Games should be fullscreen
        assert fullscreen == "1" or fullscreen.lower() == "true"
        
    def test_orientation_configured(self):
        """Test that orientation is configured"""
        config = configparser.ConfigParser()
        config.read("buildozer.spec")
        
        assert config.has_option("app", "orientation")
        orientation = config.get("app", "orientation")
        
        # Should be one of the valid orientations
        valid_orientations = ["landscape", "portrait", "sensorLandscape", "all"]
        assert orientation in valid_orientations


class TestAndroidEntryPoint:
    """Test Android entry point file"""
    
    def test_main_py_exists(self):
        """Test that main.py entry point exists"""
        assert os.path.exists("main.py"), "main.py entry point not found"
        
    def test_main_py_imports(self):
        """Test that main.py has correct imports"""
        with open("main.py", "r") as f:
            content = f.read()
        
        # Should import pywrkgame
        assert "import pywrkgame" in content or "from pywrkgame" in content
        
        # Should have error handling
        assert "try:" in content
        assert "except" in content
        
    def test_main_py_executable(self):
        """Test that main.py is syntactically correct"""
        with open("main.py", "r") as f:
            content = f.read()
        
        # Try to compile the file
        try:
            compile(content, "main.py", "exec")
        except SyntaxError as e:
            pytest.fail(f"main.py has syntax errors: {e}")


class TestAndroidDocumentation:
    """Test Android build documentation"""
    
    def test_android_build_doc_exists(self):
        """Test that Android build documentation exists"""
        assert os.path.exists("ANDROID_BUILD.md"), "ANDROID_BUILD.md not found"
        
    def test_android_build_doc_content(self):
        """Test that Android build documentation has required content"""
        with open("ANDROID_BUILD.md", "r") as f:
            content = f.read()
        
        # Should have key sections
        assert "Prerequisites" in content
        assert "Building for Android" in content
        assert "buildozer" in content.lower()
        
        # Should have build commands
        assert "buildozer android debug" in content
        assert "buildozer android release" in content
        
        # Should have troubleshooting
        assert "Troubleshooting" in content or "troubleshooting" in content
        
    def test_android_build_doc_requirements(self):
        """Test that documentation references requirements"""
        with open("ANDROID_BUILD.md", "r") as f:
            content = f.read()
        
        # Should reference Requirement 2.8
        assert "2.8" in content or "Requirement 2.8" in content


class TestBuildozerIntegration:
    """Test Buildozer integration readiness"""
    
    def test_source_files_present(self):
        """Test that required source files are present"""
        # Check for Python source
        assert os.path.exists("python"), "python directory not found"
        
        # Check for C++ source
        assert os.path.exists("src"), "src directory not found"
        assert os.path.exists("include"), "include directory not found"
        
    def test_cmake_configuration_present(self):
        """Test that CMake configuration is present"""
        assert os.path.exists("CMakeLists.txt"), "CMakeLists.txt not found"
        
    def test_setup_py_present(self):
        """Test that setup.py is present"""
        assert os.path.exists("setup.py"), "setup.py not found"
        
    def test_exclude_patterns_configured(self):
        """Test that build excludes unnecessary files"""
        config = configparser.ConfigParser()
        config.read("buildozer.spec")
        
        assert config.has_option("app", "source.exclude_dirs")
        exclude_dirs = config.get("app", "source.exclude_dirs")
        
        # Should exclude test and build directories
        assert "tests" in exclude_dirs
        assert "build" in exclude_dirs
        assert ".git" in exclude_dirs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
