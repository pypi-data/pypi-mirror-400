from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="jpcli",
    version="1.0.1",
    author="Jaime Cuevas",
    author_email="adancuevas@outlook.com",
    description="A library to convert Linux command output to JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JaimeAdanCuevas/jpcli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'jpcli=jpcli.main:main',
        ],
    },
)
