import unittest
from unittest.mock import MagicMock
from scrapers.rfnegocios import RFNegociosScraper
from core.models import Property

class TestRFNegociosNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = RFNegociosScraper()
        # Fixture baseada nos dados fornecidos
        self.fixture = {
            "data": [{
                "id": "f132e600-2dc7-45b3-b284-c99c9616960e",
                "price": "R$280.000",
                "title_formatted": "Casa à Venda no Fábio Silva",
                "url": "casa-a-venda-no-bairro-fabio-silva-em-tubarao-sc/2021307",
                "address": {"formatted": "Fábio Silva - Tubarão/SC"},
                "areas": [], # Caso de áreas vazias
                "rooms": {
                    "bedroom": {"value": 2},
                    "bathroom": {"value": 2},
                    "garage": {"value": 1}
                }
            }],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization(self):
        """Verifica se os campos da Tecimob são mapeados corretamente para Property."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.fixture
        self.scraper.client._session.get = MagicMock(return_value=mock_resp)
        
        results = self.scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertIsInstance(prop, Property)
        self.assertEqual(prop.agency, "rfnegocios")
        self.assertEqual(prop.price, 280000.0)
        self.assertIsNone(prop.area) # Lista de áreas estava vazia na fixture
        self.assertEqual(prop.bedrooms, 2)
        self.assertEqual(prop.neighborhood, "Fábio Silva")
        self.assertEqual(prop.city, "Tubarão")
        self.assertIn("rodneifrancaimoveis.com.br/comprar/", prop.url)

if __name__ == "__main__":
    unittest.main()