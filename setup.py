from setuptools import find_packages, setup

# Read the requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="crossfitgames",  # Replace with your package name
    version="2.1.0",
    description="A package for collecting CrossFit Games data",
    author="Arnar Hardarson",
    author_email="arnarhardar44@gmail.com",
    packages=find_packages(where="src"),  # Looks for packages in the "src" folder
    package_dir={"": "src"},  # Root directory for packages
    install_requires=requirements,  # Use dependencies from requirements.txt
    python_requires=">=3.9",  # Specify the required Python version
)
