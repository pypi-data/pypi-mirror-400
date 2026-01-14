from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="orrin-sdk",
    version="0.0.9",
    description="SDK for creating and registering custom Orrin apps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    author="Aidan White",
    author_email="ceo@stellr-company.com",
    license="Proprietary",  # Or "Stellr, LLC Proprietary License - See LICENSE file"
    license_files=['LICENSE'],  # Ensures the file is included in wheels/sdists
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",  # This is the standard for custom/proprietary
        "Operating System :: OS Independent",
    ],
)