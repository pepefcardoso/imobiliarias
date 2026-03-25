from scrapers.tecimob_base import TecimobScraper

BASE_URL = "https://moradaimoveistb.com.br"
API_ENDPOINT = "https://api-sites2.gerenciarimoveis-cf.com.br/api/properties"

class MoradaImoveisTbScraper(TecimobScraper):
    name = "moradaimoveistb"
    BASE_URL = BASE_URL
    API_ENDPOINT = API_ENDPOINT
    _HEADERS = {
        "x-domain": "moradaimoveistb.com.br",
        "Accept": "application/json",
        "Referer": BASE_URL + "/",
        "Origin": BASE_URL,
    }