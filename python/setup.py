import setuptools

# Load the version module to get the current version.
exec(open("jaraf/version.py").read())

# The long description comes from the README.md file.
with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jaraf-app",
    version=VERSION,
    author="Edward Labao",
    author_email="edlabao.dev@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    description="A python application framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://github.com/edlabao/jaraf-app",
    zip_safe=True
)
