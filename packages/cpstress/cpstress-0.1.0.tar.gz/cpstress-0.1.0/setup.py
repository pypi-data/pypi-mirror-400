from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cpstress",
    version="0.1.0",
    author="Srijan Verma",
    author_email="srijan@example.com",
    description="A comprehensive stress testing data generator for competitive programming with cryptographically secure randomness",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sharpsalt/cpstress",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.7",
    keywords="competitive programming test data generation random stress-testing",
    project_urls={
        "Bug Reports": "https://github.com/sharpsalt/cpstress/issues",
        "Source": "https://github.com/sharpsalt/cpstress",
    },
)
