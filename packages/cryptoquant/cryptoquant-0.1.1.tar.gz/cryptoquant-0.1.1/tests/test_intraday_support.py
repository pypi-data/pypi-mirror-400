"""
Tests for intraday data support in RequestHandler.

This module tests the validation and formatting utilities added to support
intraday (hourly) queries to the CryptoQuant API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from unittest import TestCase
from unittest.mock import MagicMock

import requests

from cryptoquant.request_handler_class.request_handler import RequestHandler


class IntradayTimestampValidationTests(TestCase):
    """Tests for timestamp validation with intraday queries."""

    def test_validate_timestamp_hour_format_valid(self) -> None:
        """Validate that proper hour format passes validation."""
        self.assertTrue(RequestHandler.validate_timestamp('20240101T120000', 'hour'))
        self.assertTrue(RequestHandler.validate_timestamp('20231231T235959', 'hour'))
        self.assertTrue(RequestHandler.validate_timestamp('20240615T000000', 'hour'))

    def test_validate_timestamp_hour_format_invalid(self) -> None:
        """Validate that improper hour format fails validation."""
        # Date-only format should fail for hour window
        self.assertFalse(RequestHandler.validate_timestamp('20240101', 'hour'))
        # Invalid formats
        self.assertFalse(RequestHandler.validate_timestamp('2024-01-01T12:00:00', 'hour'))
        self.assertFalse(RequestHandler.validate_timestamp('20240101T1200', 'hour'))

    def test_validate_timestamp_day_format_valid(self) -> None:
        """Validate that both date and datetime formats work for day window."""
        # Date-only format
        self.assertTrue(RequestHandler.validate_timestamp('20240101', 'day'))
        # Full datetime format
        self.assertTrue(RequestHandler.validate_timestamp('20240101T120000', 'day'))

    def test_validate_timestamp_invalid_dates(self) -> None:
        """Validate that invalid dates are rejected."""
        # Invalid date
        self.assertFalse(RequestHandler.validate_timestamp('20240231', 'day'))
        self.assertFalse(RequestHandler.validate_timestamp('20240231T120000', 'hour'))
        # Invalid time
        self.assertFalse(RequestHandler.validate_timestamp('20240101T250000', 'hour'))
        self.assertFalse(RequestHandler.validate_timestamp('20240101T126000', 'hour'))


class IntradayTimestampFormattingTests(TestCase):
    """Tests for timestamp formatting utilities."""

    def test_format_timestamp_from_datetime_hour(self) -> None:
        """Test formatting datetime objects for hour window."""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = RequestHandler.format_timestamp_for_window(dt, 'hour')
        self.assertEqual(result, '20240115T143045')

    def test_format_timestamp_from_datetime_day(self) -> None:
        """Test formatting datetime objects for day window."""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = RequestHandler.format_timestamp_for_window(dt, 'day')
        self.assertEqual(result, '20240115')

    def test_format_timestamp_string_date_for_day(self) -> None:
        """Test that date strings pass through for day window."""
        result = RequestHandler.format_timestamp_for_window('20240115', 'day')
        self.assertEqual(result, '20240115')

    def test_format_timestamp_string_date_for_hour_raises(self) -> None:
        """Test that date-only strings raise error for hour window."""
        with self.assertRaises(ValueError) as context:
            RequestHandler.format_timestamp_for_window('20240115', 'hour')
        self.assertIn('intraday', str(context.exception).lower())
        self.assertIn('YYYYMMDDTHHMMSS', str(context.exception))

    def test_format_timestamp_string_datetime_for_hour(self) -> None:
        """Test that full datetime strings work for hour window."""
        result = RequestHandler.format_timestamp_for_window('20240115T143045', 'hour')
        self.assertEqual(result, '20240115T143045')

    def test_format_timestamp_invalid_format_raises(self) -> None:
        """Test that invalid timestamp formats raise ValueError."""
        with self.assertRaises(ValueError):
            RequestHandler.format_timestamp_for_window('2024-01-15', 'day')
        with self.assertRaises(ValueError):
            RequestHandler.format_timestamp_for_window('invalid', 'hour')


class IntradayParameterNormalizationTests(TestCase):
    """Tests for parameter normalization with intraday queries."""

    def setUp(self) -> None:
        """Prepare a reusable request handler instance."""
        self.session = MagicMock(spec=requests.Session)
        self.handler = RequestHandler(
            api_key="test_api_key",
            session=self.session,
            default_timeout=5.0,
        )

    def _mock_response(self) -> MagicMock:
        """Create a mock HTTP response with a JSON payload."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "data": []}
        mock_response.text = '{"status": "ok", "data": []}'
        return mock_response

    def test_handle_request_hour_with_valid_timestamps(self) -> None:
        """Test that hour window with valid timestamps passes validation."""
        self.session.get.return_value = self._mock_response()

        result = self.handler.handle_request(
            "btc/exchange-flows/reserve",
            {
                "window": "hour",
                "from_": "20240101T000000",
                "to_": "20240101T120000",
                "exchange": "binance",
            },
        )

        self.session.get.assert_called_once()
        params: Dict[str, Any] = self.session.get.call_args.kwargs["params"]
        self.assertEqual(params.get("window"), "hour")
        self.assertEqual(params.get("from"), "20240101T000000")
        self.assertEqual(params.get("to"), "20240101T120000")
        self.assertEqual(result, {"status": "ok", "data": []})

    def test_handle_request_hour_with_invalid_from_timestamp_raises(self) -> None:
        """Test that hour window with invalid 'from' timestamp raises ValueError."""
        self.session.get.return_value = self._mock_response()

        with self.assertRaises(ValueError) as context:
            self.handler.handle_request(
                "btc/exchange-flows/reserve",
                {
                    "window": "hour",
                    "from_": "20240101",  # Missing time component
                    "exchange": "binance",
                },
            )

        self.assertIn("from", str(context.exception).lower())
        self.assertIn("YYYYMMDDTHHMMSS", str(context.exception))
        # Should not make API call if validation fails
        self.session.get.assert_not_called()

    def test_handle_request_hour_with_invalid_to_timestamp_raises(self) -> None:
        """Test that hour window with invalid 'to' timestamp raises ValueError."""
        self.session.get.return_value = self._mock_response()

        with self.assertRaises(ValueError) as context:
            self.handler.handle_request(
                "btc/exchange-flows/reserve",
                {
                    "window": "hour",
                    "from_": "20240101T000000",
                    "to_": "20240101",  # Missing time component
                    "exchange": "binance",
                },
            )

        self.assertIn("to", str(context.exception).lower())
        self.assertIn("YYYYMMDDTHHMMSS", str(context.exception))
        # Should not make API call if validation fails
        self.session.get.assert_not_called()

    def test_handle_request_day_with_date_only_timestamps(self) -> None:
        """Test that day window accepts date-only timestamps."""
        self.session.get.return_value = self._mock_response()

        result = self.handler.handle_request(
            "btc/exchange-flows/reserve",
            {
                "window": "day",
                "from_": "20240101",
                "to_": "20240131",
                "exchange": "binance",
            },
        )

        self.session.get.assert_called_once()
        params: Dict[str, Any] = self.session.get.call_args.kwargs["params"]
        self.assertEqual(params.get("window"), "day")
        self.assertEqual(params.get("from"), "20240101")
        self.assertEqual(params.get("to"), "20240131")
        self.assertEqual(result, {"status": "ok", "data": []})

    def test_handle_request_day_with_datetime_timestamps(self) -> None:
        """Test that day window also accepts full datetime timestamps."""
        self.session.get.return_value = self._mock_response()

        result = self.handler.handle_request(
            "btc/exchange-flows/reserve",
            {
                "window": "day",
                "from_": "20240101T000000",
                "to_": "20240131T235959",
                "exchange": "binance",
            },
        )

        self.session.get.assert_called_once()
        params: Dict[str, Any] = self.session.get.call_args.kwargs["params"]
        self.assertEqual(params.get("from"), "20240101T000000")
        self.assertEqual(params.get("to"), "20240131T235959")
        self.assertEqual(result, {"status": "ok", "data": []})

    def test_handle_request_without_window_accepts_any_format(self) -> None:
        """Test that requests without window parameter don't enforce strict validation."""
        self.session.get.return_value = self._mock_response()

        # Should work without validation errors
        result = self.handler.handle_request(
            "btc/status/entity-list",
            {
                "type_": "exchange",
            },
        )

        self.session.get.assert_called_once()
        self.assertEqual(result, {"status": "ok", "data": []})


class IntradayUseCaseTests(TestCase):
    """Integration-style tests for common intraday use cases."""

    def setUp(self) -> None:
        """Prepare a reusable request handler instance."""
        self.session = MagicMock(spec=requests.Session)
        self.handler = RequestHandler(
            api_key="test_api_key",
            session=self.session,
            default_timeout=5.0,
        )

    def _mock_response(self, data: Any = None) -> MagicMock:
        """Create a mock HTTP response."""
        if data is None:
            data = {"status": "ok", "data": []}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = data
        return mock_response

    def test_intraday_exchange_reserve_query(self) -> None:
        """Test a typical intraday query for exchange reserves."""
        self.session.get.return_value = self._mock_response()

        result = self.handler.handle_request(
            "btc/exchange-flows/reserve",
            {
                "window": "hour",
                "from_": "20240101T000000",
                "to_": "20240101T235959",
                "exchange": "binance",
                "limit": 24,
            },
        )

        self.session.get.assert_called_once()
        call_kwargs = self.session.get.call_args.kwargs
        params = call_kwargs["params"]

        # Verify all parameters are passed correctly
        self.assertEqual(params["window"], "hour")
        self.assertEqual(params["from"], "20240101T000000")
        self.assertEqual(params["to"], "20240101T235959")
        self.assertEqual(params["exchange"], "binance")
        self.assertEqual(params["limit"], 24)

    def test_intraday_netflow_query_with_csv_format(self) -> None:
        """Test intraday netflow query with CSV output."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "timestamp,netflow\n20240101T000000,100.5\n20240101T010000,150.2"
        self.session.get.return_value = mock_response

        result = self.handler.handle_request(
            "btc/exchange-flows/netflow",
            {
                "window": "hour",
                "from_": "20240101T000000",
                "to_": "20240101T020000",
                "exchange": "kraken",
                "format_": "csv",
            },
        )

        # Result should be CSV text
        self.assertIsInstance(result, str)
        self.assertIn("timestamp,netflow", result)
        self.session.get.assert_called_once()
