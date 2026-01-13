"""
Setup configuration for Theca Procurator.

This file enables building Python wheels for distribution.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from __init__.py
init_file = Path(__file__).parent / "theca_procurator" / "__init__.py"
version = "0.1.0"
for line in init_file.read_text().splitlines():
    if line.startswith("__version__"):
        version = line.split("=")[1].strip().strip('"').strip("'")
        break

# Read long description from README if available
readme_file = Path(__file__).parent.parent.parent.parent / "Docs" / "USERS GUIDE.md"
long_description = "Desktop File & Folder Utility"
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')

setup(
    name="theca-procurator",
    version=version,
    author="RH Labs/The SurveyOS Project",
    description="Desktop File & Folder Utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'theca_procurator': ['*.toml', 'plugins/*.yapsy-plugin'],
    },
    install_requires=[
        "ttkbootstrap>=1.10.1",
        "yapsy>=1.12.2",
        "toml>=0.10.2",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'mypy>=0.950',
            'flake8>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'theca-procurator=theca_procurator.main:main',
        ],
    },
    python_requires='>=3.9',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Filesystems",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
)
