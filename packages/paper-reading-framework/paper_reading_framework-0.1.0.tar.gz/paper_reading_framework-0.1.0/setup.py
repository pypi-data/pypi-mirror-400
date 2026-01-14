"""
Paper Reading Framework - 论文阅读框架
使用 Moonshot AI (Kimi) 进行论文的精度阅读、内化和落地的完整框架
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# 读取 requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="paper-reading-framework",
    version="0.1.0",
    description="使用 Moonshot AI (Kimi) 进行论文的精度阅读、内化和落地的完整框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ocarina",
    author_email="ocarina1024@gmail.com",
    url="https://github.com/ocarina1024/paper-reading-framework",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "console_scripts": [
            "paper-reading=src.main:main",
        ],
    },
    keywords="paper reading, academic research, AI analysis, Moonshot, Kimi",
    project_urls={
        "Documentation": "https://github.com/ocarina1024/paper-reading-framework",
        "Source": "https://github.com/ocarina1024/paper-reading-framework",
        "Tracker": "https://github.com/ocarina1024/paper-reading-framework/issues",
    },
)
