"""
tests/test_imobiliariaaqui.py

Unit tests for the Imobiliária Aqui scraper.
"""

import unittest
from unittest.mock import MagicMock

from scrapers.imobiliariaaqui import ImobiliariaAquiScraper, _split_address
from core.models import Property


FIXTURE = {
    "data": [
        {
            "id": "1379e998-38ee-4451-a36b-6201ded1e4c5",
            "reference": "608",
            "price": "R$280.000,00",
            "total_price": "R$280.000,00",
            "title_formatted": "Casa Mista em São Clemente, Tubarão/SC",
            "url": "casa-a-venda-sao-clemente/608",
            "address": {"formatted": "Tubarão/SC"},
            "areas": {
                "total_area": {"name": "total_area", "value": "318", "measure": "m²"},
            },
            "rooms": {
                "garage": {"value": 3},
                "bedroom": {"value": 3},
                "bathroom": {"value": 1},
            },
        },
        {
            "id": "86b60674-c1f4-48b2-8706-a36af74165f8",
            "reference": "606",
            "price": "R$289.900,00",
            "total_price": "R$289.900,00",
            "title_formatted": "Apartamento semi mobiliado no Parque das Palmeiras",
            "url": "apartamento-a-venda-no-bairro-vila-esperanca-em-tubarao-sc/606",
            "address": {"formatted": "Vila Esperança - Tubarão/SC"},
            "areas": {
                "primary_area": {"name": "private_area", "value": "52,84", "measure": "m²"},
            },
            "rooms": {
                "garage": {"value": 1},
                "bedroom": {"value": 2},
                "bathroom": {"value": 1},
            },
        },
    ],
    "meta": {
        "pagination": {
            "total": 14,
            "per_page": 21,
            "current_page": 1,
            "total_pages": 1,
        }
    },
}


class TestImobiliariaAquiNormalization(unittest.TestCase):
    def setUp(self):
        self.scraper = ImobiliariaAquiScraper()
        self.scraper._fetch_page = MagicMock(return_value=FIXTURE)

    def test_returns_correct_number_of_properties(self):
        results = self.scraper.scrape()
        self.assertEqual(len(results), 2)

    def test_all_results_are_property_instances(self):
        for prop in self.scraper.scrape():
            self.assertIsInstance(prop, Property)

    def test_agency_name(self):
        for prop in self.scraper.scrape():
            self.assertEqual(prop.agency, "imobiliariaaqui")

    def test_price_parsed(self):
        results = self.scraper.scrape()
        self.assertAlmostEqual(results[0].price, 280000.0)
        self.assertAlmostEqual(results[1].price, 289900.0)

    def test_area_prefers_total_area(self):
        results = self.scraper.scrape()
        self.assertAlmostEqual(results[0].area, 318.0)

    def test_area_falls_back_to_primary_area(self):
        results = self.scraper.scrape()
        self.assertAlmostEqual(results[1].area, 52.84)

    def test_bedrooms_parsed(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].bedrooms, 3)
        self.assertEqual(results[1].bedrooms, 2)

    def test_parking_parsed(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].parking, 3)
        self.assertEqual(results[1].parking, 1)

    def test_neighborhood_without_separator(self):
        results = self.scraper.scrape()
        # "Tubarão/SC" has no " - " separator → neighborhood is None
        self.assertIsNone(results[0].neighborhood)
        self.assertEqual(results[0].city, "Tubarão")

    def test_neighborhood_with_separator(self):
        results = self.scraper.scrape()
        self.assertEqual(results[1].neighborhood, "Vila Esperança")
        self.assertEqual(results[1].city, "Tubarão")

    def test_url_construction(self):
        results = self.scraper.scrape()
        self.assertEqual(
            results[0].url,
            "https://imobiliariaaqui.com.br/comprar/casa-a-venda-sao-clemente/608",
        )

    def test_empty_data_returns_empty_list(self):
        self.scraper._fetch_page = MagicMock(
            return_value={"data": [], "meta": {"pagination": {"total_pages": 1}}}
        )
        self.assertEqual(self.scraper.scrape(), [])


class TestSplitAddress(unittest.TestCase):
    def test_full_address(self):
        self.assertEqual(_split_address("Centro - Tubarão/SC"), ("Centro", "Tubarão"))

    def test_no_neighborhood(self):
        self.assertEqual(_split_address("Tubarão/SC"), (None, "Tubarão"))

    def test_empty_string(self):
        self.assertEqual(_split_address(""), (None, None))

    def test_complex_neighborhood(self):
        self.assertEqual(
            _split_address("São João (Margem Esquerda) - Tubarão/SC"),
            ("São João (Margem Esquerda)", "Tubarão"),
        )


if __name__ == "__main__":
    unittest.main()