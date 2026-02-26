import unittest
from unittest.mock import MagicMock
from scrapers.pauloemayer import PauloEMayerScraper
from core.models import Property

class TestPauloEMayerNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = PauloEMayerScraper()
        # Fixture baseada no JSON real fornecido pelo usuário
        self.fixture = {
            "data": [
                {
                    "price": "R$280.000,00",
                    "title_formatted": "Casa",
                    "url": "casa-a-venda-no-bairro-sao-joao-margem-esquerda-em-tubarao-sc/1213",
                    "address": {"formatted": "São João (Margem Esquerda) - Tubarão/SC"},
                    "areas": {
                        "primary_area": {"value": "70"},
                        "total_area": {"value": "300"}
                    },
                    "rooms": {
                        "garage": {"value": 1},
                        "bedroom": {"value": 2}
                    }
                },
                {
                    "price": "R$230.000,00",
                    "title_formatted": "Apartamento",
                    "url": "apartamento-a-venda-no-bairro-vila-esperanca-em-tubarao-sc/729",
                    "address": {"formatted": "Vila Esperança - Tubarão/SC"},
                    "areas": [], # Caso real onde áreas vem vazio
                    "rooms": {"bedroom": {"value": 2}, "garage": {"value": 1}}
                }
            ],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization(self):
        """Verifica se o mapeamento Tecimob -> Property está correto."""
        self.scraper._fetch_page = MagicMock(return_value=self.fixture)
        results = self.scraper.scrape()
        
        self.assertEqual(len(results), 2)
        
        # Teste Casa São João (Preferência por total_area)
        casa = results[0]
        self.assertEqual(casa.agency, "pauloemayer")
        self.assertEqual(casa.price, 280000.0)
        self.assertEqual(casa.area, 300.0) # Deve preferir total_area
        self.assertEqual(casa.neighborhood, "São João (Margem Esquerda)")
        self.assertEqual(casa.city, "Tubarão")
        self.assertIn("pauloemayer.com/comprar/", casa.url)

        # Teste Apartamento Vila Esperança (Tratamento de lista de áreas vazia)
        apto = results[1]
        self.assertEqual(apto.neighborhood, "Vila Esperança")
        self.assertIsNone(apto.area)

if __name__ == "__main__":
    unittest.main()