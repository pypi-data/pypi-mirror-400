from setuptools import setup, find_packages

# Read the contents of the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cxregions",
    version="0.1.4", 
    author="Toby Driscoll", 
    author_email="driscoll@udel.edu",  
    description="A Python interface to the ComplexRegions.jl Julia package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/complexvariables/cxregions", 
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "numpy>=1.23.5,<2",
        "juliacall>=0.9.30,<0.10"
    ],
    include_package_data=True,
)