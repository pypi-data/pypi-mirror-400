from setuptools import setup, find_packages

setup(
    name="trusted_log",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "sigstore>=1.0.0",
    ],
    python_requires='>=3.6',
    author="Siyuan Hui",
    author_email="siyuan.hui@intel.com",
    description="trusted_log provides transparency log-related APIs to complete behavioral recording throughout the entire lifecycle of Docker container images, including building, uploading, downloading, and deployment.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Hsy-Intel/trusted-log",
)
