import unittest
from unittest.mock import MagicMock
from scrapers.conquistalarimoveis import ConquistalarImoveisScraper
from core.models import Property

class TestConquistalarNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = ConquistalarImoveisScraper()
        # Fixture baseada nos dados REAIS fornecidos
        self.fixture = {
            "data": [{
                "id": "6fa07c24-5bf4-42ae-8477-cbf9e10b78f6",
                "price": "R$215.000,00",
                "title_formatted": "CASA GEMINADA DUPLEX NO BAIRRO HUMAITÁ DE CIMA",
                "url": "casa-a-venda-no-bairro-humaita-de-cima-em-tubarao-sc/472",
                "address": {"formatted": "Humaitá de Cima - Tubarão/SC"},
                "areas": {
                    "private_area": {"value": "45,18"}
                },
                "rooms": {
                    "bedroom": {"value": 1},
                    "bathroom": {"value": 1},
                    "garage": {"value": 1}
                }
            }],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization(self):
        """Verifica se o mapeamento Tecimob -> Property está correto."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.fixture
        mock_resp.raise_for_status = MagicMock()
        self.scraper.client._session.get = MagicMock(return_value=mock_resp)
        
        results = self.scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertEqual(prop.agency, "conquistalarimoveis")
        self.assertEqual(prop.price, 215000.0)
        self.assertEqual(prop.area, 45.18)
        self.assertEqual(prop.bedrooms, 1)
        self.assertEqual(prop.neighborhood, "Humaitá de Cima")
        self.assertEqual(prop.city, "Tubarão")
        self.assertEqual(prop.url, "https://conquistalarimoveis.com.br/comprar/casa-a-venda-no-bairro-humaita-de-cima-em-tubarao-sc/472")

if __name__ == "__main__":
    unittest.main()