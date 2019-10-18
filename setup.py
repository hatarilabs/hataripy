import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hataripy",
    version="0.0.8",
    author="Saul Montoya",
    author_email="saulmontoya@hatarilabs.com",
    description="An unofficial version of USGS Flopy that creates VTK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hatarilabs/hataripy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
)
