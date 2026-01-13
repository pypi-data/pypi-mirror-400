# setup.py

from setuptools import setup, find_packages

setup(
    name="osman_hadi",
    version="1.0.10",
    author="Mahdi bin iqbal",
    author_email="islammdmahadi943@gmail.com",
    description="A bilingual Python library documenting the life and legacy of Shaheed Osman Bin Hadi.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mahadi99900/Osman_Hadi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
