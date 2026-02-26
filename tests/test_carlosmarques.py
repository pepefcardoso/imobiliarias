import unittest
from unittest.mock import MagicMock
from scrapers.carlosmarques import CarlosMarquesScraper
from core.models import Property

class TestCarlosMarquesNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = CarlosMarquesScraper()
        # Mock dos dados reais fornecidos
        self.fixture = {
            "data": [
                {
                    "id": "3a955983-b883-4186-9662-272f2b9f1fc1",
                    "price": "R$190.000,00",
                    "title_formatted": "Casa de Madeira",
                    "url": "casa-a-venda-no-bairro-morrotes-em-tubarao-sc/5443",
                    "address": {"formatted": "Morrotes - Tubarão/SC"},
                    "areas": {
                        "total_area": {"value": "171,50"}
                    },
                    "rooms": {
                        "bedroom": {"value": 2},
                        "bathroom": {"value": 1},
                        "garage": {"value": 1}
                    }
                }
            ],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization_fields(self):
        """Verifica se os campos da Tecimob são mapeados corretamente para o modelo Property."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.fixture
        self.scraper.client._session.get = MagicMock(return_value=mock_resp)
        
        results = self.scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertEqual(prop.agency, "carlosmarques")
        self.assertEqual(prop.title, "Casa de Madeira")
        self.assertEqual(prop.price, 190000.0)
        self.assertEqual(prop.area, 171.5)
        self.assertEqual(prop.bedrooms, 2)
        self.assertEqual(prop.neighborhood, "Morrotes")
        self.assertEqual(prop.city, "Tubarão")
        self.assertIn("carlosmarquescorretor.com.br/comprar/", prop.url)

    def test_address_splitting(self):
        """Testa o helper de extração de bairro e cidade."""
        bairro, cidade = self.scraper._split_address("Oficinas - Tubarão/SC")
        self.assertEqual(bairro, "Oficinas")
        self.assertEqual(cidade, "Tubarão")

if __name__ == "__main__":
    unittest.main()