from setuptools import setup, find_packages

setup(
    name="county-mask-generator",
    version="0.1.0",
    description="A package to generate weight masks for regridding lat/lon data to county-level.",
    url="https://github.com/cstirry/county-mask-generator",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "xarray",
        "geopandas",
        "shapely"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
