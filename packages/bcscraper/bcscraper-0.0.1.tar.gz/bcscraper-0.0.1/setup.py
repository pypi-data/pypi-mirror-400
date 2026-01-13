"""Set up module for BCScraper"""
from setuptools import setup, find_packages

VERSION = "0.0.1"
DESCRIPTION = "Un scraper para buscacursos.uc.cl."
LONG_DESCRIPTION = "Un scraper para buscacursos.uc.cl sin usar proxies."

setup(
    name="bcscraper",
    version=VERSION,
    author="Víctor Moreno",
    author_email="vicmoor07@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.14.3",
        "cloudscraper>=1.2.71",
    ],
    keywords=["scraper", "buscacursos", "uc"]
)
