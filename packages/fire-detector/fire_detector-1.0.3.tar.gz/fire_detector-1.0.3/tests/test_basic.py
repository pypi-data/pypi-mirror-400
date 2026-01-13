import unittest
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fire_detector import FireDetector

class TestFireDetector(unittest.TestCase):
    def test_init(self):
        """Test that FireDetector initializes without error (using defaults)"""
        try:
            detector = FireDetector()
            self.assertIsNotNone(detector)
            print("\n✅ FireDetector initialized successfully")
        except Exception as e:
            self.fail(f"FireDetector initialization failed: {e}")

if __name__ == '__main__':
    unittest.main()
