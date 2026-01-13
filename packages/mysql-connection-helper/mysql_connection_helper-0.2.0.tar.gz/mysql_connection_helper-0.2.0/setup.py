from setuptools import setup, find_packages

setup(
    name="mysql-connection-helper",
    version="0.2.0",
    author="Vishva",
    author_email="vishvaiioe@gamil.com",
    description="A lightweight MySQL connection helper using mysql-connector-python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "mysql-connector-python>=8.0.0"
    ],
    extras_require={
        "dev": ["pytest"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database",
    ],
    python_requires=">=3.7",
)
