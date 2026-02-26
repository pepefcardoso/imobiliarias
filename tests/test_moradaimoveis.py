import unittest
from unittest.mock import MagicMock
from scrapers.moradaimoveis import MoradaImoveisScraper
from core.models import Property

class TestMoradaImoveisNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = MoradaImoveisScraper()
        # Fixture baseada no JSON real fornecido
        self.fixture = {
            "data": [{
                "id": "23a8adc7-9c7e-4509-9c03-b8f0e2bbd17d",
                "price": "R$298.479,00",
                "title_formatted": "Apartamento",
                "url": "apartamento-a-venda-no-bairro-oficinas-em-tubarao-sc/1270",
                "address": {"formatted": "Oficinas - Tubarão/SC"},
                "areas": {
                    "primary_area": {"value": "49,05"}
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
        """Verifica se os campos da Tecimob são mapeados corretamente para Property."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.fixture
        mock_resp.raise_for_status = MagicMock()
        self.scraper.client._session.get = MagicMock(return_value=mock_resp)
        
        results = self.scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertEqual(prop.agency, "moradaimoveis")
        self.assertEqual(prop.price, 298479.0)
        self.assertEqual(prop.area, 49.05)
        self.assertEqual(prop.bedrooms, 2)
        self.assertEqual(prop.neighborhood, "Oficinas")
        self.assertEqual(prop.city, "Tubarão")
        self.assertEqual(prop.url, "https://moradaimoveis.com.br/comprar/apartamento-a-venda-no-bairro-oficinas-em-tubarao-sc/1270")

if __name__ == "__main__":
    unittest.main()