"""
Setup configuration for ajt-grounded-extract.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme = Path("README.md").read_text(encoding="utf-8")

setup(
    name="ajt-grounded-extract",
    version="2.1.0",
    author="AJT Contributors",
    author_email="",
    description="Judgment-first grounded extraction engine. Returns ACCEPT with evidence or STOP with proof. Nothing in between.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Nick-heo-eg/ajt-grounded-extract",
    packages=find_packages(exclude=["tests", "examples", "evidence", "viewer"]),
    python_requires=">=3.7",
    install_requires=[
        # Zero dependencies - pure Python stdlib
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="audit compliance legal extraction stop-first negative-proof",
    project_urls={
        "Documentation": "https://github.com/Nick-heo-eg/ajt-grounded-extract/blob/main/README.md",
        "Source": "https://github.com/Nick-heo-eg/ajt-grounded-extract",
        "Tracker": "https://github.com/Nick-heo-eg/ajt-grounded-extract/issues",
        "Normative Spec": "https://github.com/Nick-heo-eg/ajt-spec",
        "Constitution": "https://github.com/Nick-heo-eg/ajt-grounded-extract/blob/main/ADMISSION_CONSTITUTION.md",
        "Attack Tests": "https://github.com/Nick-heo-eg/ajt-grounded-extract/blob/main/ATTACK_TEST.md",
    },
)
