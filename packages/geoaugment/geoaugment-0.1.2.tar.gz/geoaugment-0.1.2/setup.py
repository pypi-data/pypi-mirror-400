from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="geoaugment",
    version="0.1.2",
    description="Constraint-aware synthetic geospatial data augmentation engine for GeoAI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chidiebere V. Christopher",
    author_email="vchidiebere.vc@gmail.com",
    url="https://github.com/93Chidiebere/GeoAugment-Algorithm",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
        "rasterio",
        "torch",
        "torchgeo",
        "click",
        "scikit-learn",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "geoaugment=geo_augment.cli.main:main"
        ]
    },
    python_requires=">=3.10",
)
