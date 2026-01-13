from setuptools import setup, find_packages

setup(
    name="VividText",
    version="0.3.3",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0",
    ],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)