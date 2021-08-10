from setuptools import setup

__version__ = "v1.0.1"

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
)
