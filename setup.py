from setuptools import setup
long_description = ""

with open("README.md", "r", encoding="utf8") as f: long_description = f.read()

setup(
    name="Boxpy",
    version="0.0.1",
    description = "Python implementation of boxen for stylish text boxes.",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)