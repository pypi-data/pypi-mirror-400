import setuptools
import os


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="STEAM_materials",
    version=os.environ['RELEASE_NAME'],
    author="STEAM Team",
    author_email="steam-team@cern.ch",
    description="Python wrapper for the steam materials package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/steam/steam-material-library",
    keywords=['STEAM', 'API', 'MATERIALS', 'CERN'],
    install_requires=['numpy'],
    python_requires='>=3.8',
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8"
        ],
)
