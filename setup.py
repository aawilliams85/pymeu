import setuptools
import pymeu

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymeu",
    version=pymeu.__version__,
    author="aawilliams85",
    author_email="",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT License",
    url="https://github.com/aawilliams85/pymeu",
    packages=setuptools.find_packages(),
    install_requires=[
        'markdown',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.12"
    ],
)