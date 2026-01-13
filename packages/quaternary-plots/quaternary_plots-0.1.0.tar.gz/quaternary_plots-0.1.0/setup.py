from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text() if (HERE / "README.md").exists() else ""

setup(
    name="quaternary-plots",
    version="0.1.0",
    author="Oliver T. Lord",
    author_email="oliver.lord@bristol.ac.uk",
    description="A Python library for creating quaternary (tetrahedral) compositional plots",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/olivertlord/quaternary-plots",
    packages=find_packages(exclude=["tests", "examples"]),
    install_requires=[
        "numpy>=1.20.0",
        "plotly>=5.0.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    license="GPL-3.0",
)
