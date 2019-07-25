import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eldr-app",
    version="0.0.1",
    author="Ed Labao",
    author_email="edlabao.dev@gmail.com",
    description="A python application framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/edlabao/eldr-app",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
