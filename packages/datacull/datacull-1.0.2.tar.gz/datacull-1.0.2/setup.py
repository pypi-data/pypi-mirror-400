from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="datacull",
    version="1.0.2",
    author = "Atif Hassan",
    author_email = "atif.hit.hassan@gmail.com",
    description = "DataCull is a modular, light-weight data pruning library containing many dataset pruning (coreset selection) algorithm including the official Implementation of the paper, titled, RCAP: Robust, Class-Aware, Probab ilistic Dynamic Dataset Pruning",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/atif-hassan/RCAP-dynamic-dataset-pruning",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "torch",
        "tqdm",
        "numpy",
        "orjsonl"
    ]
)