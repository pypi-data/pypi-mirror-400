"""
Tests for server selection and measurement prerequisites.
"""

import asyncio
import unittest
from unittest.mock import patch
from pyasyncspeedtest import AsyncSpeedtest


class TestServerSelection(unittest.TestCase):
    """Test server selection logic and error handling."""

    def setUp(self):
        self.speedtest = AsyncSpeedtest(debug=False)

    @patch('pyasyncspeedtest.runner.speedtest.AsyncSpeedtest.fetch')
    def test_get_best_server_empty_list(self, mock_fetch):
        """get_best_server should return None when server list is empty."""
        async def run_test():
            mock_fetch.return_value = '<settings></settings>'

            result = await self.speedtest.get_best_server()

            self.assertIsNone(result)
            self.assertIsNone(self.speedtest.best_server)

        asyncio.run(run_test())

    def test_measure_latency_without_server_raises_error(self):
        """measure_latency should raise RuntimeError when no server is selected."""
        async def run_test():
            with self.assertRaises(RuntimeError) as context:
                await self.speedtest.measure_latency()
            self.assertIn("No server selected", str(context.exception))

        asyncio.run(run_test())

    def test_measure_download_without_server_raises_error(self):
        """measure_download_speed should raise RuntimeError when no server is selected."""
        async def run_test():
            with self.assertRaises(RuntimeError) as context:
                await self.speedtest.measure_download_speed()
            self.assertIn("No server selected", str(context.exception))

        asyncio.run(run_test())

    def test_measure_upload_without_server_raises_error(self):
        """measure_upload_speed should raise RuntimeError when no server is selected."""
        async def run_test():
            with self.assertRaises(RuntimeError) as context:
                await self.speedtest.measure_upload_speed()
            self.assertIn("No server selected", str(context.exception))

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
