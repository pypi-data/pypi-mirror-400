"""
A setuptools based setup module for the 'dataframe-inspector' project.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dataframe-inspector",
    version="0.1.2",
    author="Canxiu Zhang",
    author_email="canxiu.z@gmail.com",
    description="Inspect nested JSON/dict structures in pandas DataFrame columns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/canxiu-zhang/dataframe-inspector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
    ],
    extras_require={  # type: ignore[arg-type]
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "pylint>=2.0",
            "mypy>=0.900",
            "mlflow>=3.0",
        ],
    },
    keywords="dataframe column inspector pandas nested json dict schema exploration eda",
)

# TODO sync dev requirements
# from pathlib import Path

# def load_requirements(path):
#     return Path(path).read_text().splitlines()

# extras_require = {
#     "dev": load_requirements("requirements-dev.txt"),
#     "gpu": load_requirements("requirements-gpu.txt"),
# }
