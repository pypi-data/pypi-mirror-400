from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="hardware-panel",
    version="1.0.1",
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