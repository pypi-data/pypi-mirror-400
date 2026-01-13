from setuptools import setup, find_packages
from pathlib import Path

# Get the long description from README.md
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "A Python wrapper for ClickHouse database operations"

# Get requirements from requirements.txt
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
        # Filter out test dependencies (pytest, pytest-cov)
        requirements = [req for req in requirements if not req.startswith("pytest")]
else:
    # Fallback if requirements.txt is not found
    requirements = [
        "clickhouse-connect>=0.6.0",
        "pandas>=1.5.0",
        "numpy>=1.20.0",
        "pyarrow>=10.0.0",
    ]

setup(
    name="chpy-orm",
    version="0.2.1",
    author="Javad Alipanah",
    author_email="javadalipanah@gmail.com",
    description="A Python wrapper for ClickHouse database operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Javad-Alipanah/chpy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
)

