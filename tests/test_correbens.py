import unittest
from unittest.mock import MagicMock
from scrapers.correbens import CorrebensScraper
from core.models import Property

class TestCorrebensNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = CorrebensScraper()
        # Fixture baseada nos dados reais fornecidos
        self.fixture = {
            "data": [{
                "id": "34913065-0fed-44d1-bbfd-805bab254cae",
                "price": "R$285.900,00",
                "title_formatted": "Apartamento",
                "meta_title": "Apartamento à venda no bairro São João (Margem Esquerda) em Tubarão/SC",
                "url": "apartamento-a-venda-no-bairro-sao-joao-margem-esquerda-em-tubarao-sc/621",
                "address": {"formatted": "São João (Margem Esquerda) - Tubarão/SC"},
                "areas": {
                    "primary_area": {"value": "41,84"}
                },
                "rooms": {
                    "bedroom": {"value": 2},
                    "bathroom": {"value": 1},
                    "garage": {"value": 1}
                }
            }],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization(self):
        """Verifica se os campos da Correbens são mapeados corretamente para Property."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.fixture
        mock_resp.raise_for_status = MagicMock()
        self.scraper.client._session.get = MagicMock(return_value=mock_resp)
        
        results = self.scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertEqual(prop.agency, "correbens")
        self.assertEqual(prop.price, 285900.0)
        self.assertEqual(prop.area, 41.84)
        self.assertEqual(prop.bedrooms, 2)
        self.assertEqual(prop.neighborhood, "São João (Margem Esquerda)")
        self.assertEqual(prop.city, "Tubarão")
        self.assertIn("correbens.com.br/comprar/", prop.url)

if __name__ == "__main__":
    unittest.main()