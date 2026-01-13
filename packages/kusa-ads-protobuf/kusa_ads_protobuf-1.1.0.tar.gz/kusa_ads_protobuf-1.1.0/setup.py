# Setup script for the myproject package
from setuptools import setup, find_packages

setup(
    name='kusa-ads-protobuf',
    version='1.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='KUSA ADS Team',
    author_email='hai.l@kusaauto.com',
    description='A package for KUSA ADS protobuf definitions',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/kusa-ads/kusa-ads-protobuf',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
