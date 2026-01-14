from setuptools import setup

setup(
    name="cloudprime",
    version="1.1.1",
    packages=["cloudprime"],
    install_requires=["requests"],
    description="A Python package for effortless file uploads and management via the CloudPrime, supporting images, videos, documents, presentations, spreadsheets, and all file types.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="IP Softech - Pratham Pansuriya",
    author_email="ipsoftechsolutions@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)