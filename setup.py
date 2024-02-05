import setuptools
import pymetransfer

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymetransfer",
    version=pymetransfer.__version__,
    author="aawilliams85",
    author_email="",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT License",
    url="https://github.com/aawilliams85/pymetransfer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.12"
    ],
)