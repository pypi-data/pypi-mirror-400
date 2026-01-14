#!/usr/bin/env python3
"""
Setup script for PyWRKGame 3.0.2
"""

from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
import os
import sys

# Check for required C++ dependencies
def check_cpp_dependencies():
    """Check if required C++ libraries are available"""
    missing_deps = []
    
    # Try to compile a simple test to check for GLM
    try:
        import tempfile
        import subprocess
        
        test_code = """
        #include <glm/glm.hpp>
        int main() { return 0; }
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            f.write(test_code)
            test_file = f.name
        
        try:
            # Try to compile the test file
            result = subprocess.run(
                ['cl.exe' if sys.platform == 'win32' else 'g++', '-c', test_file, '-o', test_file + '.o'],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                missing_deps.append('GLM (OpenGL Mathematics)')
        except:
            missing_deps.append('GLM (OpenGL Mathematics)')
        finally:
            try:
                os.unlink(test_file)
                if os.path.exists(test_file + '.o'):
                    os.unlink(test_file + '.o')
            except:
                pass
    except:
        pass
    
    if missing_deps:
        error_msg = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    MISSING C++ DEPENDENCIES                                ║
╚════════════════════════════════════════════════════════════════════════════╝

PyWRKGame requires the following C++ libraries to be installed:
  • GLM (OpenGL Mathematics)
  • Box2D (2D Physics)
  • Bullet3 (3D Physics)

Please install them before installing PyWRKGame:

Windows (vcpkg):
  git clone https://github.com/Microsoft/vcpkg.git
  cd vcpkg
  .\\bootstrap-vcpkg.bat
  .\\vcpkg install glm box2d bullet3
  .\\vcpkg integrate install

Linux (Ubuntu/Debian):
  sudo apt-get update
  sudo apt-get install libglm-dev libbox2d-dev libbullet-dev build-essential

macOS:
  brew install glm box2d bullet

After installing dependencies, try again:
  pip install pywrkgame

For more information, visit:
  https://github.com/surgik-gh/pywrkgame#installation

"""
        print(error_msg, file=sys.stderr)
        # Don't fail immediately - let the build try and show the actual error
        # sys.exit(1)

# Run dependency check
check_cpp_dependencies()

# Read the README for long description
def read_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "PyWRKGame 3.0.0 - High-performance game engine with Python bindings"

# Define the extension module
ext_modules = [
    Pybind11Extension(
        "pywrkgame",
        [
            "python/bindings.cpp",
            "python/core_bindings.cpp", 
            "python/rendering_bindings.cpp",
            "python/physics_bindings.cpp",
            "python/audio_bindings.cpp",
            "python/ui_bindings.cpp",
            # Core sources
            "src/core/EngineCore.cpp",
            "src/core/EntityManager.cpp",
            "src/core/ComponentManager.cpp",
            "src/core/SystemManager.cpp",
            "src/core/PerformanceOptimizer.cpp",
            # Platform sources
            "src/platform/PlatformManager.cpp",
            "src/platform/TouchInputManager.cpp",
            # Rendering sources
            "src/rendering/RenderingEngine.cpp",
            "src/rendering/GraphicsDevice.cpp",
            "src/rendering/VulkanDevice.cpp",
            "src/rendering/D3D12Device.cpp",
            "src/rendering/MetalDevice.cpp",
            "src/rendering/PBRRenderer.cpp",
            "src/rendering/GlobalIllumination.cpp",
            "src/rendering/PostProcessing.cpp",
            "src/rendering/ParticleSystem.cpp",
            "src/rendering/LODSystem.cpp",
            # Animation sources
            "src/animation/AnimationSystem.cpp",
            "src/animation/IKSolver.cpp",
            "src/animation/ProceduralAnimation.cpp",
            # Physics sources
            "src/physics/PhysicsEngine.cpp",
            "src/physics/Box2DBackend.cpp",
            "src/physics/Bullet3Backend.cpp",
            # Audio sources
            "src/audio/AudioSystem.cpp",
            # Network sources
            "src/network/NetworkManager.cpp",
            # AI sources
            "src/ai/AIFramework.cpp",
            # Assets sources
            "src/assets/AssetManager.cpp",
            # UI sources
            "src/ui/UISystem.cpp",
            # Memory sources
            "src/memory/MemoryManager.cpp",
            # Tools sources
            "src/tools/PerformanceProfiler.cpp",
            "src/tools/DebugTools.cpp",
        ],
        include_dirs=[
            "include",
            pybind11.get_include(),
        ],
        language='c++',
        cxx_std=17,
    ),
]

setup(
    name="pywrkgame",
    version="3.0.3",
    author="WorkerAI",
    author_email="workerai@gmail.com",
    url="https://github.com/your-org/pywrkgame",
    description="High-performance game engine with Python bindings for 2D/3D games",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "pybind11>=2.6.0",
        "glm",
        "box2d",
        "bullet3",
    ],
    extras_require={
        "test": ["pytest>=6.0", "hypothesis>=6.0"],
        "dev": ["pytest>=6.0", "hypothesis>=6.0", "cmake>=3.16"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    keywords="game engine gamedev 2d 3d graphics physics audio mobile cross-platform",
    project_urls={
        "Documentation": "https://github.com/your-org/pywrkgame/tree/main/docs",
        "Source": "https://github.com/your-org/pywrkgame",
        "Bug Reports": "https://github.com/your-org/pywrkgame/issues",
    },
)