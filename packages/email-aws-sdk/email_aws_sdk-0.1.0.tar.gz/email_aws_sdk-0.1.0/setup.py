from setuptools import setup, find_packages

setup(
    name="email-aws-sdk",
    version="0.1.0",
    author="Smit Vekariya",
    description="Custom AWS SDK wrapper over boto3",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.40.60"
    ],
    python_requires=">=3.13.9",
)