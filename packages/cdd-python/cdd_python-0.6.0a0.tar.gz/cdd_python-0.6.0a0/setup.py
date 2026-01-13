from setuptools import setup, find_packages
import os

# On s'assure que les binaires sont inclus dans la distribution
package_data = {
    'cdd': ['bin/ratel.exe', 'bin/ratel'],
}

setup(
    name="cdd-python",
    version="0.6.0a0",
    author="Fabio Meyer<github.com/jemmyx>",
    description="Python adapter for the CDD Security Framework (Ratel Core)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cdd-framework/cdd-python",
    packages=find_packages(),
    # this must exist to include the ratel binaries
    package_data=package_data,
    include_package_data=True,
    install_requires=[
        # List of python deps...
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
