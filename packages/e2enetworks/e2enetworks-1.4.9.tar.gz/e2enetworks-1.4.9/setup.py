from setuptools import setup
from setuptools import find_packages
from os import path

version = "1.4.9"
install_requires = [
    "requests",
    "urllib3",
    "minio",
    "prettytable",
    "tqdm",
    "pyyaml",
    "datasets>=3.0.0",
    "transformers>=4.44.0",
    "s3fs>=2024.6.1"
]
# read the contents of your README file

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.rst")) as f:
    long_description = f.read()

setup(
    name="e2enetworks",
    version=version,
    description="E2E Networks TIR Plugins",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="E2E Networks",
    license="MIT",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
)
