"""
scrapers/juliocorretor.py
Scraper para Júlio Teixeira Corretor (https://juliocorretor.com.br).
Platform: Tecimob (api-sites2).
"""
from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://juliocorretor.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class JulioCorretorScraper(TecimobScraper):
    name = "juliocorretor"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    default_sort = "-is_price_shown,-calculated_price,id"
    _HEADERS = {
        "x-domain": "juliocorretor.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }