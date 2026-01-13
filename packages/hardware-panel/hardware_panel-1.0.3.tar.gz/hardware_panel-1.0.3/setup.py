from setuptools import setup, find_packages
from pathlib import Path
import os

# README for PyPI long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Get icon files
icon_files = []
icons_dir = this_directory / "icons"
if icons_dir.exists():
    icon_files = [f"icons/{f.name}" for f in icons_dir.glob("*.svg")]

setup(
    name="hardware-panel",
    version="1.0.3",
    author="Martim 'martimmpr' Ribeiro",
    description="Powerful system monitoring and hardware control application for Linux.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/martimmpr/linux-hardware-panel",
    project_urls={
        "Bug Tracker": "https://github.com/martimmpr/linux-hardware-panel/issues",
        "Source Code": "https://github.com/martimmpr/linux-hardware-panel",
        "Changelog": "https://github.com/martimmpr/linux-hardware-panel/blob/main/CHANGELOG.md",
    },
    license="MIT",
    py_modules=["hardware_panel"],
    data_files=[
        (os.path.join("share", "hardware-panel", "icons"), [os.path.join("icons", f) for f in os.listdir("icons") if f.endswith(".svg")]),
    ],
    package_data={
        "": ["icons/*.svg"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Hardware",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt5>=5.15.0",
        "psutil>=5.8.0",
        "pyqtgraph>=0.12.0",
    ],
    entry_points={
        "console_scripts": [
            "hardware-panel=hardware_panel:main",
            "hwpanel=hardware_panel:main",
        ],
    },
)