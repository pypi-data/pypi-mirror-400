import unittest
import numpy as np
from src.corrupt_tta import corrupt, corruption_dict
import time

class TestRigorous(unittest.TestCase):
    def setUp(self):
        # Standard ImageNet size
        self.img_std = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        # Non-standard size
        self.img_large = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)
        self.img_small = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        # Grayscale (simulated as 3-channel)
        self.img_gray = np.zeros((224, 224, 3), dtype=np.uint8)
        self.img_gray[:,:,0] = self.img_gray[:,:,1] = self.img_gray[:,:,2] = np.random.randint(0, 256, (224, 224), dtype=np.uint8)

    def test_image_sizes(self):
        """Test that corruptions handle various image sizes correctly."""
        test_sizes = [(64, 64, 3), (224, 224, 3), (299, 299, 3), (512, 512, 3)]
        for size in test_sizes:
            img = np.random.randint(0, 256, size, dtype=np.uint8)
            for name in ["gaussian_noise", "defocus_blur", "snow", "brightness"]:
                with self.subTest(size=size, corruption=name):
                    corrupted = corrupt(img, severity=1, corruption_name=name)
                    self.assertEqual(corrupted.shape, size)

    def test_data_types(self):
        """Test that corruptions handle different input data types (float vs uint8)."""
        img_float = self.img_std.astype(np.float32)
        for name in ["gaussian_noise", "gaussian_blur", "contrast"]:
            with self.subTest(corruption=name):
                # The library expects [0, 255] range even for floats
                corrupted = corrupt(img_float, severity=1, corruption_name=name)
                self.assertEqual(corrupted.shape, self.img_std.shape)
                self.assertTrue(np.max(corrupted) <= 255.1) # Allow for small float precision

    def test_statistical_change(self):
        """Verify that corruptions actually change the image data."""
        for name, func in corruption_dict.items():
            with self.subTest(corruption=name):
                corrupted = func(self.img_std, severity=3)
                # Check that the image is actually different
                diff = np.abs(self.img_std.astype(float) - corrupted.astype(float))
                self.assertGreater(np.mean(diff), 0, f"Corruption {name} did not change the image.")

    def test_severity_monotonicity(self):
        """Verify that higher severity generally leads to more change (statistical check)."""
        # Using Gaussian Noise as a representative
        diffs = []
        for s in range(1, 6):
            corrupted = corrupt(self.img_std, severity=s, corruption_name="gaussian_noise")
            diff = np.mean(np.abs(self.img_std.astype(float) - corrupted.astype(float)))
            diffs.append(diff)
        
        # Check if diffs are generally increasing
        for i in range(len(diffs) - 1):
            self.assertLessEqual(diffs[i], diffs[i+1], f"Severity {i+2} is not more intense than {i+1}")

    def test_performance(self):
        """Measure execution time for a batch of corruptions."""
        start_time = time.time()
        for _ in range(10):
            corrupt(self.img_std, severity=3, corruption_name="motion_blur")
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        print(f"\nAverage execution time for motion_blur: {avg_time:.4f}s")
        self.assertLess(avg_time, 0.5) # Should be reasonably fast

if __name__ == '__main__':
    unittest.main()
