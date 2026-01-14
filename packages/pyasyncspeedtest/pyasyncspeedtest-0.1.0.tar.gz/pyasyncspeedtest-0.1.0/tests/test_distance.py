"""
Tests for geographic distance calculations.
"""

import unittest
from pyasyncspeedtest.runner._internal import calculate_distance


class TestDistanceCalculation(unittest.TestCase):
    """Test Haversine distance calculation."""

    def test_calculate_distance_ny_to_london(self):
        """Distance between New York and London should be approximately 5570 km."""
        ny_lat, ny_lon = 40.7128, -74.0060
        london_lat, london_lon = 51.5074, -0.1278

        distance = calculate_distance(ny_lat, ny_lon, london_lat, london_lon)

        # Check that distance is approximately correct (within 100 km tolerance)
        self.assertGreater(distance, 5400)
        self.assertLess(distance, 5700)

    def test_calculate_distance_same_point(self):
        """Distance between identical coordinates should be 0."""
        distance = calculate_distance(40.7128, -74.0060, 40.7128, -74.0060)
        self.assertAlmostEqual(distance, 0.0, places=5)

    def test_calculate_distance_antipodal(self):
        """Distance between antipodal points should be approximately half Earth's circumference."""
        # Test with roughly opposite points
        lat1, lon1 = 0.0, 0.0
        lat2, lon2 = 0.0, 180.0

        distance = calculate_distance(lat1, lon1, lat2, lon2)

        # Half of Earth's circumference is approximately 20,000 km
        self.assertGreater(distance, 19000)
        self.assertLess(distance, 21000)


if __name__ == "__main__":
    unittest.main()
