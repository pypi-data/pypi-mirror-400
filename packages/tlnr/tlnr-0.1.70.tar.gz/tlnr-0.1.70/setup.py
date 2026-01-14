"""Setup script for tlnr."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""
except (UnicodeDecodeError, FileNotFoundError):
    long_description = ""

setup(
    name="tlnr",
    version="0.1.70",
    author="Jatin Mayekar",
    author_email="jatin@tlnr.dev",
    description="TLNR (Too Long; No Need To Read) - Real-time terminal command education for Zsh",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jatinmayekar/tlnr",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "tlnr": ["data/*.json", "*.zsh"],
    },
    extras_require={
        "dev": ["pytest", "twine", "build"],
        "local-llm": [],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Intended Audience :: Developers",
        "Topic :: System :: Shells",
        "Topic :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=[
        "rich>=10.0.0",
        "requests>=2.25.0",
        "cryptography>=41.0.0",
        "openai>=1.0.0",
        "importlib_resources>=5.0.0; python_version < '3.9'",
        "llama-cpp-python>=0.2.70",
        "huggingface-hub>=0.23.0",
    ],
    entry_points={
        "console_scripts": [
            "tlnr=tlnr.cli:main",
        ],
    },
    keywords="terminal, cli, learning, commands, tutorial, zsh, shell, education, real-time, tlnr, tldr",
    license="AGPL-3.0",
)