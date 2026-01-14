import setuptools
from pathlib import Path

setuptools.setup(
    name="davidpdf3",
    version=1.1,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"])
)