from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="beam-clipboard",
    version="0.2.0",
    author="vw2x",
    description="Cross-device clipboard tool via cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vwww-droid/Beam",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
    extras_require={
        "clipboard": ["pyperclip>=1.8.0"],
    },
    entry_points={
        "console_scripts": [
            "bm=beam.cli:main",
        ],
    },
)

