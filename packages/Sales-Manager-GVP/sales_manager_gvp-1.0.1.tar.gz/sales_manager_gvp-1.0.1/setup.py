from setuptools import setup, find_packages

setup(
    name = "Sales_Manager_GVP",
    version = "1.0.1",
    author = "Martín Guevara Ulloa",
    author_email = "msgu0603@gmail.com",
    description = "This package provides functionalities for managing sales, including price calculations, taxes, and discounts.",
    long_description = open("README.md", encoding="utf-8").read(),
    long_description_content_type = "text/markdown",
    url = ("https://github.com/msgu0603-code/Sales-Manager"),
    packages = find_packages(),
    install_requires = [],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires = ">= 3.7"
)