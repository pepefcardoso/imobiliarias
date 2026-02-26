import unittest
from unittest.mock import MagicMock
from scrapers.imobiliariaacacia import ImobiliariaAcaciaScraper
from core.models import Property

class TestImobiliariaAcaciaNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = ImobiliariaAcaciaScraper()
        # Mock do JSON baseado no exemplo fornecido pelo utilizador
        self.fixture = {
            "data": [{
                "id": "a68fa4ce-1ded-40b8-a3e4-87dc52695ba6",
                "price": "R$300.000",
                "address": {"formatted": "Centro - Tubarão/SC"},
                "areas": {
                    "total_area": {"value": "68", "measure": "m²"},
                    "primary_area": {"value": "55", "measure": "m²"}
                },
                "rooms": {
                    "bedroom": {"value": 2},
                    "bathroom": {"value": 2},
                    "garage": {"value": 1}
                },
                "title_formatted": "Apartamento em Centro, Tubarão/SC",
                "url": "apartamento-a-venda-no-bairro-centro-em-tubarao-sc/1272"
            }],
            "meta": {"pagination": {"total_pages": 1}}
        }

    def test_normalization_maps_fields_correctly(self):
        """Verifica se os campos da Tecimob são mapeados corretamente para Property."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = self.fixture
        mock_resp.raise_for_status = MagicMock()
        self.scraper.client._session.get = MagicMock(return_value=mock_resp)
        
        results = self.scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        
        self.assertEqual(prop.agency, "imobiliariaacacia")
        self.assertEqual(prop.price, 300000.0)
        self.assertEqual(prop.area, 68.0) # Prefere total_area
        self.assertEqual(prop.bedrooms, 2)
        self.assertEqual(prop.bathrooms, 2)
        self.assertEqual(prop.neighborhood, "Centro")
        self.assertEqual(prop.city, "Tubarão")
        self.assertIn("imobiliariaacacia.com.br/comprar/", prop.url)

    def test_handle_empty_areas(self):
        """Testa o caso em que 'areas' vem como lista vazia (conforme o JSON da Acácia)."""
        fixture_empty_areas = self.fixture.copy()
        fixture_empty_areas["data"][0]["areas"] = []
        
        self.scraper._fetch_page = MagicMock(return_value=fixture_empty_areas)
        results = self.scraper.scrape()
        self.assertIsNone(results[0].area)

if __name__ == "__main__":
    unittest.main()