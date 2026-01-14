#!/usr/bin/env python3
"""
Setup script for rchf (Custom Rich Help Formatter)

This provides backward compatibility for tools that still use setup.py
Modern builds should use pyproject.toml with hatchling.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List
import traceback

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Error: setuptools is required to install rchf")
    print("Please install it first: pip install setuptools")
    sys.exit(1)

# Read the long description from README.md
def read_long_description() -> str:
    """Read the long description from README.md."""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        try:
            return readme_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: Could not read README.md: {e}")
    return "Custom Rich Help Formatter - A beautifully styled argparse formatter with rich formatting and multi-config support"

def get_version0() -> str:
    """Extract version from pyproject.toml."""
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    if pyproject_path.exists():
        try:
            content = pyproject_path.read_text(encoding="utf-8")
            # Look for version in pyproject.toml
            version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if version_match:
                return version_match.group(1)
        except Exception as e:
            print(f"Warning: Could not read version from pyproject.toml: {e}")
    
    # Fallback to default version
    return "1.0.0"
    
def get_version():
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return get_version0()

def get_requirements() -> List[str]:
    """Extract requirements from pyproject.toml."""
    requirements = []
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    
    if pyproject_path.exists():
        try:
            content = pyproject_path.read_text(encoding="utf-8")
            # Find dependencies section
            in_deps = False
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("dependencies"):
                    in_deps = True
                    continue
                elif in_deps and line.startswith("["):
                    # New section started
                    break
                elif in_deps and line and not line.startswith("#"):
                    # Remove brackets and quotes
                    req = line.strip('[]", ')
                    if req and not req.startswith("#"):
                        requirements.append(req)
        except Exception as e:
            print(f"Warning: Could not read requirements from pyproject.toml: {e}")
    
    # Fallback to minimum requirements
    if not requirements:
        requirements = [
            "rich>=13.0.0",
            "rich-argparse>=1.0.0",
            "envdot>=0.1.0",
        ]
    
    return requirements

def get_optional_requirements() -> Dict[str, List[str]]:
    """Extract optional requirements from pyproject.toml."""
    extras_require = {}
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    
    if pyproject_path.exists():
        try:
            content = pyproject_path.read_text(encoding="utf-8")
            # Find optional dependencies section
            lines = content.splitlines()
            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith("[project.optional-dependencies]"):
                    # Parse optional dependencies
                    current_extra = None
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j].strip()
                        if next_line.startswith("["):
                            # New section started
                            break
                        elif next_line.endswith("=") and next_line.startswith("["):
                            # Found an extra
                            current_extra = next_line.strip('[]= ')
                            extras_require[current_extra] = []
                        elif current_extra and next_line and not next_line.startswith("#"):
                            # Add requirement to current extra
                            req = next_line.strip('", ')
                            if req and not req.startswith("#"):
                                extras_require[current_extra].append(req)
                    break
        except Exception as e:
            print(f"Warning: Could not read optional requirements from pyproject.toml: {e}")
    
    # Fallback to dev requirements
    if not extras_require:
        extras_require = {
            "dev": [
                "pytest>=7.0.0",
                "pytest-cov>=4.0.0",
                "black>=23.0.0",
                "isort>=5.12.0",
                "mypy>=1.0.0",
                "ruff>=0.1.0",
            ]
        }
    
    return extras_require

def get_classifiers() -> List[str]:
    """Get PyPI classifiers."""
    return [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Utilities",
    ]

def get_keywords() -> List[str]:
    """Get package keywords."""
    return [
        "argparse",
        "rich",
        "formatter",
        "cli",
        "help",
        "terminal",
        "stylish",
        "color",
        "formatting",
    ]

def get_project_urls() -> Dict[str, str]:
    """Get project URLs."""
    return {
        "Homepage": "https://github.com/cumulus13/rchf",
        "Repository": "https://github.com/cumulus13/rchf",
        "Bug Tracker": "https://github.com/cumulus13/rchf/issues",
        "Documentation": "https://github.com/cumulus13/rchf#readme",
    }

def get_entry_points() -> Dict[str, List[str]]:
    """Get console script entry points."""
    return {
        "console_scripts": [
            "rchf-demo = rchf.demo:main",
            "rchf = rchf.demo:main",
        ]
    }

# Package metadata
NAME = "rchf"
VERSION = get_version()
DESCRIPTION = "Custom Rich Help Formatter - A beautifully styled argparse formatter with rich formatting and multi-config support"
LONG_DESCRIPTION = read_long_description()
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"
AUTHOR = "Hadi Cahyadi"
AUTHOR_EMAIL = "cumulus13@gmail.com"
URL = "https://github.com/cumulus13/rchf"
LICENSE = "MIT"
PACKAGES = find_packages(include=["rchf", "rchf.*"])
PYTHON_REQUIRES = ">=3.8"
INSTALL_REQUIRES = get_requirements()
EXTRAS_REQUIRE = get_optional_requirements()
CLASSIFIERS = get_classifiers()
KEYWORDS = get_keywords()
PROJECT_URLS = get_project_urls()
ENTRY_POINTS = get_entry_points()

# Package data
PACKAGE_DATA = {
    "rchf": ["py.typed"],  # For type checking support
}

# Setup configuration
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    project_urls=PROJECT_URLS,
    entry_points=ENTRY_POINTS,
    
    # Additional metadata
    zip_safe=False,
    include_package_data=True,
    
    # Options for development
    test_suite="tests",
    
    # For backwards compatibility
    setup_requires=["setuptools>=61.0.0", "wheel"],
)

if __name__ == "__main__":
    print(f"Setting up {NAME} v{VERSION}")
    print(f"Python {sys.version}")
    print(f"Platform: {sys.platform}")