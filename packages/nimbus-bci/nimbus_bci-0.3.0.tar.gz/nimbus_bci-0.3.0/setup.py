"""
Setup script for Nimbus PySDK with Cython compilation.

This script compiles the proprietary core algorithms to binary extensions
for IP protection. The compiled extensions are platform-specific (.so on
Linux/macOS, .pyd on Windows).

Usage:
    # Development install (source, no compilation)
    pip install -e .

    # Build compiled extensions only
    python setup.py build_ext --inplace

    # Build wheel with compiled extensions
    python setup.py bdist_wheel

    # Clean compiled files
    python setup.py clean --all

Environment Variables:
    NIMBUS_INCLUDE_SOURCE=1  Include source files in wheel (for debugging)
"""

import os
import shutil
import sys
from pathlib import Path

from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py

# Check if Cython is available
try:
    from Cython.Build import cythonize
    from Cython.Distutils import Extension

    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False
    Extension = None
    cythonize = None

# Define which modules should be compiled (proprietary core algorithms)
PROTECTED_MODULES = [
    # LDA model - Bayesian conjugate learning and inference
    "nimbus_bci/models/nimbus_lda/learning",
    "nimbus_bci/models/nimbus_lda/inference",
    # QDA model - Class-conditional Gaussian with per-class covariance
    "nimbus_bci/models/nimbus_qda/learning",
    "nimbus_bci/models/nimbus_qda/inference",
    # Softmax model - Polya-Gamma variational inference
    "nimbus_bci/models/nimbus_softmax/learning",
    "nimbus_bci/models/nimbus_softmax/inference",
    # STS model - Extended Kalman Filter with state dynamics
    "nimbus_bci/models/nimbus_sts/learning",
    "nimbus_bci/models/nimbus_sts/inference",
]

# Convert to module names for exclusion
PROTECTED_MODULE_NAMES = [p.replace("/", ".") for p in PROTECTED_MODULES]

# Check if we should include source (for debugging)
INCLUDE_SOURCE = os.environ.get("NIMBUS_INCLUDE_SOURCE", "0") == "1"

# Exclude source files for protected modules only when explicitly requested.
# This avoids broken installs when extension compilation is skipped or fails.
EXCLUDE_SOURCE = os.environ.get("NIMBUS_EXCLUDE_SOURCE", "0") == "1"

# Updated by OptionalBuildExt to indicate whether extension compilation succeeded.
EXTENSIONS_BUILT = False


def get_extensions():
    """Build list of Cython extensions from protected modules."""
    if not CYTHON_AVAILABLE:
        return []

    extensions = []
    base_dir = Path(__file__).parent

    for module_path in PROTECTED_MODULES:
        # Check for .pyx first, fall back to .py
        pyx_file = base_dir / f"{module_path}.pyx"
        py_file = base_dir / f"{module_path}.py"

        if pyx_file.exists():
            source_file = str(pyx_file)
        elif py_file.exists():
            source_file = str(py_file)
        else:
            print(f"Warning: Source file not found for {module_path}")
            continue

        # Convert path to module name
        module_name = module_path.replace("/", ".")

        ext = Extension(
            name=module_name,
            sources=[source_file],
            # Compiler directives for optimization
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        )
        extensions.append(ext)

    return extensions


class ExcludeProtectedSourceBuildPy(build_py):
    """Custom build_py that excludes source files for compiled modules."""

    def find_package_modules(self, package, package_dir):
        """Override to exclude protected module source files."""
        modules = super().find_package_modules(package, package_dir)
        
        # Safety first:
        # - If Cython isn't available, we must ship Python sources.
        # - If extensions didn't build, we must ship Python sources.
        # - Only exclude when explicitly requested for production wheels.
        if INCLUDE_SOURCE or (not EXCLUDE_SOURCE) or (not CYTHON_AVAILABLE) or (not EXTENSIONS_BUILT):
            return modules
        
        # Filter out protected modules (their .so files will be included instead)
        filtered = []
        for pkg, mod, filepath in modules:
            full_module = f"{pkg}.{mod}" if pkg else mod
            if full_module in PROTECTED_MODULE_NAMES:
                print(f"  Excluding source: {full_module} (compiled extension provided)")
            else:
                filtered.append((pkg, mod, filepath))
        
        return filtered


class OptionalBuildExt(build_ext):
    """Custom build_ext that handles missing Cython gracefully."""

    def run(self):
        global EXTENSIONS_BUILT
        EXTENSIONS_BUILT = False

        if not CYTHON_AVAILABLE:
            print("=" * 60)
            print("Cython not available - skipping extension compilation")
            print("Install Cython with: pip install Cython>=3.0")
            print("=" * 60)
            return

        # Check if any source files exist
        if not self.extensions:
            print("No extension modules to build")
            return

        try:
            super().run()
            EXTENSIONS_BUILT = True
        except Exception as e:
            print(f"Warning: Failed to build extensions: {e}")
            print("Falling back to pure Python implementation")

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except Exception as e:
            print(f"Warning: Failed to build {ext.name}: {e}")


def main():
    """Main setup function."""
    extensions = get_extensions()

    # Cythonize if available and extensions exist
    if CYTHON_AVAILABLE and extensions:
        extensions = cythonize(
            extensions,
            compiler_directives={
                "language_level": "3",
                "boundscheck": False,
                "wraparound": False,
                "initializedcheck": False,
                "cdivision": True,
                # Embed source in docstrings for debugging (disable in production)
                "embedsignature": True,
            },
            # Don't generate .c files in source tree
            build_dir="build/cython",
        )

    setup(
        # Package discovery
        packages=find_packages(where="."),
        package_dir={"": "."},
        # Include compiled extensions
        ext_modules=extensions,
        cmdclass={
            "build_ext": OptionalBuildExt,
            "build_py": ExcludeProtectedSourceBuildPy,
        },
        # Include package data (compiled .so/.pyd files)
        include_package_data=True,
        package_data={
            "nimbus_bci": [
                "*.so",
                "*.pyd",
                "models/*/*.so",
                "models/*/*.pyd",
            ]
        },
        # Exclude Cython intermediates
        exclude_package_data={
            "": ["*.pyx", "*.c", "*.html"],
        },
        # ZIP-safe must be False for compiled extensions
        zip_safe=False,
    )


if __name__ == "__main__":
    main()


