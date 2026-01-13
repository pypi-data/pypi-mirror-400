import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="argumentor_gardehal",
    version="0.0.2",
    author="Gardehal",
    author_email="alethogar@protonmail.com",
    description="CLI argument parsing, validation, documentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gardehal/argumentor",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
