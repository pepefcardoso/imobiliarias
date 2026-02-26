"""
tests/test_dubettuimoveis.py

Unit tests for the Dubettu Imóveis scraper.

Strategy:
  - Uses a JSON fixture matching the Imobzi API response format.
  - Mocks the HTTP session — no live network calls.
  - Validates normalization, pagination, and edge cases.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.settings import AgencyConfig
from core.models import Property
from scrapers.dubettuimoveis import DubettuImoveisScraper


# ---------------------------------------------------------------------------
# Fixtures — shaped like real Imobzi API responses
# ---------------------------------------------------------------------------

def _make_listing(**overrides) -> dict:
    base = {
        "db_id": 4507889385865216,
        "code": "1540",
        "sale_value": 230000.0,
        "rental_value": 0.0,
        "property_type": "Apartamento",
        "finality": "residential",
        "bedroom": 2,
        "bathroom": 1,
        "garage": 1,
        "suite": 0,
        "useful_area": 46.0,
        "area": 46.0,
        "lot_area": 0.0,
        "neighborhood": "Monte Castelo",
        "city": "Tubarão",
        "state": "SC",
        "country": "Brasil",
        "site_url": "/imovel/apartamento-2-quartos-monte-castelo-tubarao-1-vaga-46m2-code-1540",
        "site_title": "Apartamento Torre Castelo a venda! Imperdível",
        "stage": "ready",
        "tags": ["sale"],
        "status": "available",
        "building": False,
        "building_name": "Residencial Torre Castelo",
        "vacation_rental": False,
    }
    base.update(overrides)
    return base


def _make_response(listings: list, cursor: str | None = None) -> dict:
    return {
        "properties": {
            "count": len(listings),
            "cursor": cursor,
            "properties": listings,
        }
    }


def _make_mock_response(payload: dict) -> MagicMock:
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = payload
    return mock


def _make_scraper(max_pages: int = 10) -> DubettuImoveisScraper:
    config = AgencyConfig(
        name="dubettuimoveis",
        url="https://www.dubettuimoveis.com.br",
        use_browser=False,
        max_pages=max_pages,
    )
    return DubettuImoveisScraper(config=config)


# ---------------------------------------------------------------------------
# Normalization tests
# ---------------------------------------------------------------------------

class TestDubettuNormalization(unittest.TestCase):

    def setUp(self):
        self.scraper = _make_scraper()
        payload = _make_response([_make_listing(), _make_listing(
            db_id=6645903560015872,
            code="1778",
            sale_value=230000.0,
            useful_area=50.0,
            area=50.0,
            bedroom=2,
            bathroom=1,
            garage=1,
            neighborhood="Santo Antonio de Padua",
            site_url="/imovel/apartamento-2-quartos-santo-antonio-de-padua-tubarao-1-vaga-code-1778",
            site_title="Apartamento 02 Dorm. em Santo Antonio de Padua - Tubarão",
        )])
        self.scraper.client._session.get = MagicMock(
            return_value=_make_mock_response(payload)
        )

    def test_returns_correct_count(self):
        self.assertEqual(len(self.scraper.scrape()), 2)

    def test_all_are_property_instances(self):
        for prop in self.scraper.scrape():
            self.assertIsInstance(prop, Property)

    def test_agency_name(self):
        for prop in self.scraper.scrape():
            self.assertEqual(prop.agency, "dubettuimoveis")

    def test_price_mapped(self):
        results = self.scraper.scrape()
        self.assertAlmostEqual(results[0].price, 230000.0)
        self.assertAlmostEqual(results[1].price, 230000.0)

    def test_useful_area_preferred(self):
        results = self.scraper.scrape()
        self.assertAlmostEqual(results[0].area, 46.0)
        self.assertAlmostEqual(results[1].area, 50.0)

    def test_bedrooms_parsed(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].bedrooms, 2)

    def test_bathrooms_parsed(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].bathrooms, 1)

    def test_parking_parsed(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].parking, 1)

    def test_neighborhood_set(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].neighborhood, "Monte Castelo")
        self.assertEqual(results[1].neighborhood, "Santo Antonio de Padua")

    def test_city_set(self):
        for prop in self.scraper.scrape():
            self.assertEqual(prop.city, "Tubarão")

    def test_url_construction(self):
        results = self.scraper.scrape()
        self.assertEqual(
            results[0].url,
            "https://www.dubettuimoveis.com.br/imovel/apartamento-2-quartos-monte-castelo-tubarao-1-vaga-46m2-code-1540",
        )

    def test_title_set(self):
        results = self.scraper.scrape()
        self.assertEqual(results[0].title, "Apartamento Torre Castelo a venda! Imperdível")

    def test_zero_useful_area_falls_back_to_area(self):
        """useful_area=0 should fall back to area field."""
        self.scraper.client._session.get = MagicMock(
            return_value=_make_mock_response(_make_response([
                _make_listing(useful_area=0.0, area=70.0)
            ]))
        )
        results = self.scraper.scrape()
        self.assertAlmostEqual(results[0].area, 70.0)

    def test_zero_both_areas_returns_none(self):
        self.scraper.client._session.get = MagicMock(
            return_value=_make_mock_response(_make_response([
                _make_listing(useful_area=0.0, area=0.0)
            ]))
        )
        results = self.scraper.scrape()
        self.assertIsNone(results[0].area)


# ---------------------------------------------------------------------------
# Pagination tests
# ---------------------------------------------------------------------------

class TestDubettuPagination(unittest.TestCase):

    def test_single_page_when_no_cursor_returned(self):
        """No cursor in response → only one request made."""
        scraper = _make_scraper()
        mock_get = MagicMock(
            return_value=_make_mock_response(_make_response([_make_listing()]))
        )
        scraper.client._session.get = mock_get
        scraper.scrape()
        self.assertEqual(mock_get.call_count, 1)

    def test_follows_cursor_to_second_page(self):
        """A non-null cursor on page 1 triggers a second request."""
        fake_cursor = "eyJhbGciOiJIUzI1NiJ9.fake"
        responses = [
            _make_mock_response(_make_response([_make_listing()], cursor=fake_cursor)),
            _make_mock_response(_make_response([_make_listing(code="9999")])),
        ]
        scraper = _make_scraper()
        scraper.client._session.get = MagicMock(side_effect=responses)
        results = scraper.scrape()
        self.assertEqual(scraper.client._session.get.call_count, 2)
        self.assertEqual(len(results), 2)

    def test_cursor_passed_as_query_param_on_page_2(self):
        """The cursor token must appear in params on the second call."""
        fake_cursor = "eyJhbGciOiJIUzI1NiJ9.fake"
        responses = [
            _make_mock_response(_make_response([_make_listing()], cursor=fake_cursor)),
            _make_mock_response(_make_response([])),
        ]
        scraper = _make_scraper()
        mock_get = MagicMock(side_effect=responses)
        scraper.client._session.get = mock_get
        scraper.scrape()

        _, kwargs2 = mock_get.call_args_list[1]
        self.assertEqual(kwargs2["params"]["cursor"], fake_cursor)

    def test_stops_at_max_pages(self):
        """Pagination must not exceed config.max_pages regardless of cursors."""
        always_cursor = "eyJhbGciOiJIUzI1NiJ9.always"
        infinite_page = _make_mock_response(
            _make_response([_make_listing()], cursor=always_cursor)
        )
        scraper = _make_scraper(max_pages=3)
        scraper.client._session.get = MagicMock(return_value=infinite_page)
        scraper.scrape()
        self.assertEqual(scraper.client._session.get.call_count, 3)

    def test_empty_listings_stops_pagination(self):
        scraper = _make_scraper()
        scraper.client._session.get = MagicMock(
            return_value=_make_mock_response(_make_response([]))
        )
        results = scraper.scrape()
        self.assertEqual(results, [])


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestDubettuEdgeCases(unittest.TestCase):

    def test_listing_without_site_url_is_skipped(self):
        scraper = _make_scraper()
        scraper.client._session.get = MagicMock(
            return_value=_make_mock_response(_make_response([
                _make_listing(site_url="")
            ]))
        )
        self.assertEqual(scraper.scrape(), [])

    def test_missing_optional_fields_return_none(self):
        minimal = {
            "db_id": 1,
            "code": "X",
            "sale_value": None,
            "useful_area": None,
            "area": None,
            "bedroom": None,
            "bathroom": None,
            "garage": None,
            "neighborhood": None,
            "city": None,
            "site_url": "/imovel/minimal-x",
            "site_title": "",
        }
        scraper = _make_scraper()
        scraper.client._session.get = MagicMock(
            return_value=_make_mock_response(_make_response([minimal]))
        )
        results = scraper.scrape()
        self.assertEqual(len(results), 1)
        prop = results[0]
        self.assertIsNone(prop.price)
        self.assertIsNone(prop.area)
        self.assertIsNone(prop.bedrooms)
        self.assertIsNone(prop.bathrooms)
        self.assertIsNone(prop.parking)
        self.assertIsNone(prop.neighborhood)
        self.assertIsNone(prop.city)

    def test_x_headers_set_on_session(self):
        scraper = _make_scraper()
        self.assertEqual(
            scraper.client._session.headers.get("Origin"),
            "https://www.dubettuimoveis.com.br",
        )


if __name__ == "__main__":
    unittest.main()