# corrupt_tta

`corrupt_tta` is a modernized Python library for applying image corruptions, based on the original ImageNet-C benchmark. It has been rewritten to use modern APIs (OpenCV, Scikit-Image, NumPy) and removes outdated dependencies like `Wand` (ImageMagick).

## Installation

```bash
pip install corrupt_tta
```

## Usage

```python
import numpy as np
from PIL import Image
from corrupt_tta import corrupt

# Load an image
img = np.array(Image.open("example.jpg"))

# Apply a corruption (e.g., Gaussian Noise with severity 3)
corrupted_img = corrupt(img, severity=3, corruption_name="gaussian_noise")

# Save or display the result
Image.fromarray(corrupted_img.astype(np.uint8)).save("corrupted.jpg")
```

### Available Corruptions

- **Noise:** `gaussian_noise`, `shot_noise`, `impulse_noise`, `speckle_noise`
- **Blur:** `gaussian_blur`, `glass_blur`, `defocus_blur`, `motion_blur`, `zoom_blur`
- **Weather:** `fog`, `frost`, `snow`
- **Digital:** `contrast`, `brightness`, `saturate`, `jpeg_compression`, `pixelate`, `elastic_transform`

## License

MIT
