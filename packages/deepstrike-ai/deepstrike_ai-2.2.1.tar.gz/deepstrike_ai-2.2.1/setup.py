from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="deepstrike-ai",
    version="2.1.0",
    author="DeepStrike Team",
    author_email="support@deepstrike.ai",
    description="Autonomous AI Pentest Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/deepstrike-ai",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.7.0",
        "click>=8.1.0",
        "openai>=1.3.7",
        "anthropic>=0.3.0",
        "cryptography>=41.0",
        "paramiko>=3.4.0",
        "PySocks>=1.7.1",
        "stem>=1.8.1",
        "mnemonic>=0.20",
        "eth-account>=0.9.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "mypy>=1.0",
            "pre-commit>=3.0",
        ],
        "termux": [
            "requests==2.31.0",
            "rich==13.7.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "deepstrike=deepstrike.ui.cli:cli",
        ],
    },
)
