"""Funciones auxiliares"""
import cloudscraper

URL = "https://buscacursos.uc.cl"
scraper = cloudscraper.create_scraper()


def fetch_html(url: str):
    """Fetchea un HTML desde Buscacursos usando Cloudscraper."""
    response = scraper.get(url)
    response.raise_for_status()
    return response.text
