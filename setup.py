from setuptools import setup
import os
from pathlib import Path

__version__ = "v1.0.0"

base_dir = os.path.dirname(os.path.realpath(__file__))
requirements_path = Path(base_dir, "requirements.txt")
install_requires = []
if os.path.isfile(requirements_path):
    with open(requirements_path) as f:
        install_requires = f.read().splitlines()

setup(
    name="spatial_ops",
    version=__version__,
    description="Utilities for working with shapefiles relating to L8 and S2 products.",
    url="https://github.com/sscullen/spatial_ops.git",
    author="Shaun Cullen",
    author_email="shaun@cullen.io",
    license="MIT",
    packages=["spatial_ops"],
    zip_safe=False,
    install_requires=install_requires,
)
