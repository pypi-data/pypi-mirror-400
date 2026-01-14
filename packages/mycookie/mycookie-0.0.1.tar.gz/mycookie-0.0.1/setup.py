from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mycookie",
    version="0.0.1",
    author="ByteBreach",
    author_email="mrfidal@proton.me",
    description="Extract cookies from URLs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bytebreach/mycookie",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0"
    ],
)