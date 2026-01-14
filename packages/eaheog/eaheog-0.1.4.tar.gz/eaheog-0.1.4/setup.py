import os
from setuptools import setup, find_packages

# Read README if available
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="eaheog",
    version="0.1.4",  # Increment this version for every update
    author="HK Pandey",
    description="EOG-HPO Client SDK for intelligent hyperparameter recommendations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "viz": ["pandas", "numpy", "matplotlib", "ipython"]
    },
)