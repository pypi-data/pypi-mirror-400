import unittest
import numpy as np
from src.corrupt_tta import corrupt, corruption_tuple, corruption_dict

class TestCorruptions(unittest.TestCase):
    def setUp(self):
        # Create a dummy image (224x224x3)
        self.img = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)

    def test_all_corruptions_run(self):
        """Test that every corruption function can be called without error."""
        for name, func in corruption_dict.items():
            with self.subTest(corruption=name):
                # Test with severity 1
                corrupted = func(self.img, severity=1)
                self.assertEqual(corrupted.shape, self.img.shape)
                self.assertTrue(np.max(corrupted) <= 255)
                self.assertTrue(np.min(corrupted) >= 0)

    def test_corrupt_wrapper_by_name(self):
        """Test the corrupt() wrapper function using names."""
        corrupted = corrupt(self.img, severity=2, corruption_name="gaussian_noise")
        self.assertEqual(corrupted.shape, self.img.shape)

    def test_corrupt_wrapper_by_number(self):
        """Test the corrupt() wrapper function using numbers."""
        corrupted = corrupt(self.img, severity=2, corruption_number=0)
        self.assertEqual(corrupted.shape, self.img.shape)

    def test_invalid_inputs(self):
        """Test that invalid inputs raise appropriate errors."""
        with self.assertRaises(ValueError):
            corrupt(self.img, severity=1) # Missing name and number

    def test_severities(self):
        """Test different severity levels for a sample corruption."""
        for s in range(1, 6):
            corrupted = corrupt(self.img, severity=s, corruption_name="brightness")
            self.assertEqual(corrupted.shape, self.img.shape)

if __name__ == '__main__':
    unittest.main()
