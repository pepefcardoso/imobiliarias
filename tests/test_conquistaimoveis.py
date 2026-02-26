import unittest
from unittest.mock import MagicMock
from scrapers.conquistaimoveis import ConquistaImoveisScraper
from core.models import Property

class TestConquistaNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = ConquistaImoveisScraper()
        # Fixture com dois cenários: areas vazias e areas preenchidas
        self.fixture = {
            "data": [
                {
                    "price": "R$299.000,00",
                    "title_formatted": "Apartamento em Centro, Tubarão/SC",
                    "url": "apartamento-a-venda-no-bairro-centro-em-tubarao-sc/209",
                    "address": {"formatted": "Centro - Tubarão/SC"},
                    "areas": [], # Cenário 1: lista vazia
                    "rooms": {"bedroom": {"value": 2}, "bathroom": {"value": 1}, "garage": {"value": 1}}
                },
                {
                    "price": "R$240.000,00",
                    "url": "apartamento-a-venda-no-bairro-sao-joao-margem-esquerda-em-tubarao-sc/141",
                    "address": {"formatted": "São João (Margem Esquerda) - Tubarão/SC"},
                    "areas": {"primary_area": {"value": "49,76"}}, # Cenário 2: dicionário
                    "rooms": {"bedroom": {"value": 2}, "bathroom": {"value": 1}, "garage": {"value": 1}}
                }
            ],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization_with_empty_and_filled_areas(self):
        self.scraper._fetch_page = MagicMock(return_value=self.fixture)
        results = self.scraper.scrape()
        
        self.assertEqual(len(results), 2)
        
        # Valida item 1 (Sem área)
        self.assertIsNone(results[0].area)
        self.assertEqual(results[0].price, 299000.0)
        self.assertEqual(results[0].neighborhood, "Centro")
        
        # Valida item 2 (Com área)
        self.assertEqual(results[1].area, 49.76)
        self.assertEqual(results[1].price, 240000.0)
        self.assertEqual(results[1].neighborhood, "São João (Margem Esquerda)")

if __name__ == "__main__":
    unittest.main()