from setuptools import setup
import pymeu

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='pymeu',
    version=pymeu.__version__,
    author='aawilliams85',
    author_email='',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT License',
    url='https://github.com/aawilliams85/pymeu',
    packages=['pymeu'],
    install_requires=[
        'pycomm3>=1.2.14'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.12'
    ]
)