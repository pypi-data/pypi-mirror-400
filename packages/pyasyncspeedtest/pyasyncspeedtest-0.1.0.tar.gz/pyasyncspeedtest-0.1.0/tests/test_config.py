"""
Tests for configuration fetching and parsing.
"""

import asyncio
import unittest
from unittest.mock import patch
from pyasyncspeedtest import AsyncSpeedtest


class TestConfiguration(unittest.TestCase):
    """Test configuration fetching and parsing."""

    def setUp(self):
        self.speedtest = AsyncSpeedtest(debug=False)

    def test_initialization(self):
        """AsyncSpeedtest should initialize with correct default values."""
        self.assertIsNone(self.speedtest.best_server)
        self.assertEqual(self.speedtest.download, 0.0)
        self.assertEqual(self.speedtest.upload, 0.0)
        self.assertEqual(self.speedtest.ping, 0.0)
        self.assertEqual(self.speedtest.public_ip, "")
        self.assertEqual(self.speedtest.isp, "")
        self.assertIsNone(self.speedtest.lat)
        self.assertIsNone(self.speedtest.lon)

    @patch('pyasyncspeedtest.runner.speedtest.AsyncSpeedtest.fetch')
    def test_get_config_success(self, mock_fetch):
        """Config parsing should extract IP, lat, lon, and ISP from valid XML."""
        async def run_test():
            mock_fetch.return_value = '''
                <client ip="1.2.3.4" lat="40.7128" lon="-74.0060" isp="Test ISP" />
            '''

            result = await self.speedtest.get_config()

            self.assertTrue(result)
            self.assertEqual(self.speedtest.public_ip, "1.2.3.4")
            self.assertEqual(self.speedtest.lat, 40.7128)
            self.assertEqual(self.speedtest.lon, -74.0060)
            self.assertEqual(self.speedtest.isp, "Test ISP")

        asyncio.run(run_test())

    @patch('pyasyncspeedtest.runner.speedtest.AsyncSpeedtest.fetch')
    def test_get_config_malformed_xml(self, mock_fetch):
        """Config parsing should return False for malformed XML."""
        async def run_test():
            mock_fetch.return_value = '<invalid>xml</invalid>'

            result = await self.speedtest.get_config()

            self.assertFalse(result)
            self.assertIsNone(self.speedtest.lat)
            self.assertIsNone(self.speedtest.lon)

        asyncio.run(run_test())

    def test_source_address_stored(self):
        """Source address parameter should be stored correctly."""
        st = AsyncSpeedtest(source_address="192.168.1.100")
        self.assertEqual(st.source_address, "192.168.1.100")

    def test_no_source_address_returns_none_connector(self):
        """Connector should be None when no source address is provided."""
        st = AsyncSpeedtest()
        connector = st._get_connector()
        self.assertIsNone(connector)


if __name__ == "__main__":
    unittest.main()
