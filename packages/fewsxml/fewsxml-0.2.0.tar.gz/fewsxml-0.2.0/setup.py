from setuptools import setup, find_packages

setup(
    name="fewsxml",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["pydantic"],
    include_package_data=True,
    author="Farid Alavi",
    author_email="farid.alavi@deltares.nl",
    description="A library for reading and writing XML files to interact with Delft-FEWS.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/FaridAlavi/fewsxml",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
