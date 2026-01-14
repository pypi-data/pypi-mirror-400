"""
Setup script for the maq-rai-sdk package.
This script uses setuptools to package the maq-rai-sdk library, which contains modules for faster Copilot Development.
Attributes:
    name (str): The name of the package.
    version (str): The current version of the package.
    description (str): A brief description of the package.
    author (str): The name of the author or the team responsible for the package.
    author_email (str): The email address of the author or the team.
    url (str): The URL of the repository (to be replaced with the actual URL).
    packages (list): A list of all Python import packages that should be included in the distribution package.
    package_dir (dict): A mapping of package names to directories.
    install_requires (list): A list of packages that are required for this package to work.
    classifiers (list): A list of classifiers that provide some additional metadata about the package.
    python_requires (str): The Python version required for this package.
"""

from setuptools import setup, find_packages

setup(
    name="maq-rai-sdk",
    version="0.2.0",
    description="RAI Package contains a Prompt Reviewer and Updater and test case generator for faster Copilot Development",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="MAQ Software",
    author_email="customersuccess@maqsoftware.com",
    url="https://github.com/MAQ-Software-Solutions/maqraisdk",
    packages=find_packages(where="MAQ_RAI_SDK"),
    package_dir={"": "MAQ_RAI_SDK"},
    include_package_data=True,
    package_data={
        # Include all yaml files in any config directory under maq_rai_sdk
        "maq_rai_sdk": ["config/*.yaml", "py.typed"],
    },
    install_requires=[
        "crewai[tools]==0.120.1",
        "types-PyYAML==6.0.12.20250516",
        "PyYAML==6.0.2",
        "onnxruntime==1.22.0",
        "azure-core>=1.26.0",
        "isodate>=0.6.1"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11", 
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["ai", "copilot", "prompt", "testing", "rai", "agent"],
    python_requires=">=3.10,<3.13",
)
