import unittest
from unittest.mock import MagicMock
from scrapers.citymoveis import CityMoveisScraper
from core.models import Property

class TestCityMoveisNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = CityMoveisScraper()
        # Fixture baseada no JSON fornecido (ID: 44e09217...)
        self.fixture = {
            "data": [{
                "price": "R$280.000,00",
                "title_formatted": "Apartamento",
                "url": "apartamento-a-venda-no-bairro-centro-em-tubarao-sc/182",
                "address": {"formatted": "Centro - Tubarão/SC"},
                "areas": {
                    "built_area": {"value": "80"},
                    "primary_area": {"value": "70"}
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
        """Valida se os dados da City Imóveis são mapeados corretamente."""
        self.scraper._fetch_page = MagicMock(return_value=self.fixture)
        
        results = self.scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertEqual(prop.agency, "citymoveis")
        self.assertEqual(prop.price, 280000.0)
        self.assertEqual(prop.area, 70.0) # Pegou primary_area pois total_area não existe
        self.assertEqual(prop.bedrooms, 1)
        self.assertEqual(prop.neighborhood, "Centro")
        self.assertEqual(prop.city, "Tubarão")
        self.assertIn("citymoveis.com.br/comprar/", prop.url)

if __name__ == "__main__":
    unittest.main()