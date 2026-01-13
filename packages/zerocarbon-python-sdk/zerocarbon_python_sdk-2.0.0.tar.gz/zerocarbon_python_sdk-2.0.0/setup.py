from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zerocarbon-python-sdk",
    version="2.0.0",
    author="ZeroCarbon.codes",
    author_email="support@zerocarbon.codes",
    description="Official Python SDK for ZeroCarbon.codes API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zerocarbon/python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/zerocarbon/python-sdk/issues",
        "Documentation": "https://zerocarbon.codes/docs/sdk/python",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "mypy>=0.950",
        ],
        "pandas": [
            "pandas>=1.3.0",
        ],
    },
)
