# tests/test_artlogs.py
import unittest
from artlogs import ArtLogProfile

class TestArtLogs(unittest.TestCase):
    def test_profile_creation(self):
        profile = ArtLogProfile()
        result = profile.logUser("testuser", "testpass", "c")
        self.assertTrue(profile.access)
        self.assertEqual(profile.username, "testuser")