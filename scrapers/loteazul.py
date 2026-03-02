from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://loteazul.com.br"
API_ENDPOINT = "https://api-sites.gerenciarimoveis-cf.com.br/api/properties"

class LoteAzulScraper(TecimobScraper):
    name = "loteazul"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    default_sort = "-updated_at,id"
    _HEADERS = {
        "x-domain": "loteazul.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }