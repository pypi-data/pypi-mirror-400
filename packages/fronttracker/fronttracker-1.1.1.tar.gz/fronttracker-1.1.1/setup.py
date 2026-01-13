from setuptools import setup, find_packages

setup(
    name="fronttracker",
    version="1.1.1",
    author="Emmanuel Romero",
    author_email="romeroqe@gmail.com",
    description="Library for detection and monitoring of ocean fronts",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/romeroqe/fronttracker",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "geopy",
        "scipy",
        "scikit-learn",
        "scikit-image",
        "shapely",
        "alphashape",
        "matplotlib"
    ],
    license="GPL-3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)