###########################################################
# Colorprint- Python module that lets you print colorfully#
# Under MIT license CoolGuy158-Git                        #
###########################################################
from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="py-colorprint-cg",
    version="0.3.3",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CoolGuy158-Git",
    url="https://github.com/CoolGuy158-Git/colorprint",
    license="MIT",
    python_requires='>=3.7',
    keywords="terminal color print ANSI style",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

