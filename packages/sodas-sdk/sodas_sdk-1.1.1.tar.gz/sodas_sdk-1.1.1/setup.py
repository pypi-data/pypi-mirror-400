from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sodas-sdk",
    version="1.1.1",
    author="SODAS Team",
    author_email="",
    description="Legacy Python SDK for the SODAS Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(
        include=["sodas_sdk", "sodas_sdk.*"],
        exclude=["sodas_sdk.tests", "sodas_sdk.tests.*"],
    ),
    package_data={"sodas_sdk": ["py.typed"]},
    package_dir={"": "."},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=["requests>=2.25.0", "pydantic>=2.0.0", "python-dateutil"],
)
