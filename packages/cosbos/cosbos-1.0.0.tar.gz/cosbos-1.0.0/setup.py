from setuptools import setup, find_packages
import os

def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    here = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(here, filename)
    lineiter = (line.strip() for line in open(file_path))
    return [line for line in lineiter if line and not line.startswith("#") and "pytest" not in line]

setup(
    name="cosbos",
    version="1.0.0",
    description="COlor-Sensor-Based Occupancy Sensing",
    long_description=open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")).read(),
    long_description_content_type="text/markdown",
    author="Quan Wang",
    url="https://github.com/wq2012/COSBOS",
    package_dir={"": "python"},
    packages=find_packages(where="python"),
    install_requires=parse_requirements("requirements.txt"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
