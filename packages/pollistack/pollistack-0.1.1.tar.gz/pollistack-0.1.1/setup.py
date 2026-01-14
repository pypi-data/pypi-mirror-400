from setuptools import setup, find_packages

setup(
    name="pollistack",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.23.0",
    ],
    author="PolliStack Team",
    description="Python SDK for PolliStack Agent Engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pollistack/pollistack",
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
