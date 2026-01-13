#!/usr/bin/env python3
from setuptools import setup, find_packages
import os
import re

def get_version():
    """Extract version from BSG_IDE.py"""
    try:
        with open('BSG_IDE.py', 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'self\.__version__\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
    except Exception:
        pass
    return "4.6.2"

def get_long_description():
    """Read long description from README"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "Beamer Slide Generator IDE"

setup(
    name="bsg-ide",
    version=get_version(),
    description="Beamer Slide Generator IDE - Integrated development environment for creating LaTeX Beamer presentations",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Ninan Sajeeth Philip",
    author_email="nsp@airis4d.com",
    url="https://github.com/sajeethphilip/Beamer-Slide-Generator",
    packages=find_packages(),
    py_modules=["BSG_IDE", "BeamerSlideGenerator"],
    include_package_data=True,
    package_data={
        '': ['*.png', '*.txt', '*.md', 'requirements.txt'],
    },
    entry_points={
        'console_scripts': [
            'bsg-ide=BSG_IDE:main',
        ],
        'gui_scripts': [
            'bsg-ide-gui=BSG_IDE:main',
        ]
    },
    install_requires=[
        # Core GUI - keep these minimal
        "customtkinter>=5.2.2",
        "Pillow>=10.0.0",

        # Media handling - make optional or lazy load
        "requests>=2.31.0",

        # PDF processing
        "PyMuPDF>=1.23.7",

        # Spell checking
        "pyspellchecker>=0.7.2",

        # Grammarly integration - ADD THIS LINE
        "grammarly-sdk>=0.5.0",  # or whatever the correct package name is
    ],
    extras_require={
        'full': [
            # Heavy dependencies - only install if explicitly requested
            "opencv-python>=4.8.0",
            "yt-dlp>=2023.11.16",
            "screeninfo>=0.8.1",
            "numpy>=1.24.0",
            "pyautogui>=0.9.54",
            "latexcodec>=2.0.1",
            "latex>=0.7.0",
        ],
        'dev': [
            # Development tools - separate from main package
            "black>=22.3.0",
            "mypy>=0.961",
            "pylint>=2.13.9",
            "qdarkstyle>=3.0.2",
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Office/Business",
        "Topic :: Multimedia :: Graphics :: Presentation",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    keywords="latex beamer presentation slides ide editor",
    project_urls={
        "Bug Reports": "https://github.com/sajeethphilip/Beamer-Slide-Generator/issues",
        "Source": "https://github.com/sajeethphilip/Beamer-Slide-Generator",
        "Documentation": "https://github.com/sajeethphilip/Beamer-Slide-Generator/wiki",
    },
)
