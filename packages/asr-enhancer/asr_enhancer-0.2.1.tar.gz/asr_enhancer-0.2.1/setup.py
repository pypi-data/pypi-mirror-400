"""
Setup configuration for asr-enhancer package.
"""

from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="asr-enhancer",
    version="0.2.1",
    author="Krishna Bajpai, Vedanshi Gupta",
    description="ASR Quality Enhancement Layer with gap detection, secondary ASR, and LLM polish",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/asr-enhancer",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "mypy>=1.0",
            "ruff>=0.1.0",
        ],
        "api": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "asr-enhancer=asr_enhancer.api.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "asr_enhancer": ["config/*.yaml", "py.typed"],
    },
)
