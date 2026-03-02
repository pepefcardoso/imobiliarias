from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://imobicasa.com.br"
API_ENDPOINT = "https://api-sites.gerenciarimoveis-cf.com.br/api/properties"

class ImobicasaScraper(TecimobScraper):
    name = "imobicasa"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "imobicasa.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }