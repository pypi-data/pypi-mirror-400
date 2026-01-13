import numpy as np
import cv2
from PIL import Image as PILImage
from scipy.ndimage import zoom as scizoom
from scipy.ndimage import map_coordinates
from skimage.filters import gaussian
from skimage.color import rgb2hsv, hsv2rgb
from skimage.util import random_noise
import os
from importlib import resources

# /////////////// Corruption Helpers ///////////////

def disk(radius, alias_blur=0.1, dtype=np.float32):
    if radius <= 8:
        L = np.arange(-8, 8 + 1)
        ksize = (3, 3)
    else:
        L = np.arange(-radius, radius + 1)
        ksize = (5, 5)
    X, Y = np.meshgrid(L, L)
    aliased_disk = np.array((X ** 2 + Y ** 2) <= radius ** 2, dtype=dtype)
    aliased_disk /= np.sum(aliased_disk)
    return cv2.GaussianBlur(aliased_disk, ksize=ksize, sigmaX=alias_blur)

def plasma_fractal(mapsize=256, wibbledecay=3):
    assert (mapsize & (mapsize - 1) == 0)
    maparray = np.empty((mapsize, mapsize), dtype=float)
    maparray[0, 0] = 0
    stepsize = mapsize
    wibble = 100

    def wibbledmean(array):
        return array / 4 + wibble * np.random.uniform(-wibble, wibble, array.shape)

    def fillsquares():
        cornerref = maparray[0:mapsize:stepsize, 0:mapsize:stepsize]
        squareaccum = cornerref + np.roll(cornerref, shift=-1, axis=0)
        squareaccum += np.roll(squareaccum, shift=-1, axis=1)
        maparray[stepsize // 2:mapsize:stepsize, stepsize // 2:mapsize:stepsize] = wibbledmean(squareaccum)

    def filldiamonds():
        mapsize_local = maparray.shape[0]
        drgrid = maparray[stepsize // 2:mapsize_local:stepsize, stepsize // 2:mapsize_local:stepsize]
        ulgrid = maparray[0:mapsize_local:stepsize, 0:mapsize_local:stepsize]
        ldrsum = drgrid + np.roll(drgrid, 1, axis=0)
        lulsum = ulgrid + np.roll(ulgrid, -1, axis=1)
        ltsum = ldrsum + lulsum
        maparray[0:mapsize_local:stepsize, stepsize // 2:mapsize_local:stepsize] = wibbledmean(ltsum)
        tdrsum = drgrid + np.roll(drgrid, 1, axis=1)
        tulsum = ulgrid + np.roll(ulgrid, -1, axis=0)
        ttsum = tdrsum + tulsum
        maparray[stepsize // 2:mapsize_local:stepsize, 0:mapsize_local:stepsize] = wibbledmean(ttsum)

    while stepsize >= 2:
        fillsquares()
        filldiamonds()
        stepsize //= 2
        wibble /= wibbledecay

    maparray -= maparray.min()
    return maparray / maparray.max()

def clipped_zoom(img, zoom_factor):
    h, w = img.shape[:2]
    ch = int(np.ceil(h / zoom_factor))
    cw = int(np.ceil(w / zoom_factor))
    top = (h - ch) // 2
    left = (w - cw) // 2
    
    if len(img.shape) == 3:
        img_cropped = img[top:top + ch, left:left + cw, :]
        zoom_tuple = (zoom_factor, zoom_factor, 1)
    else:
        img_cropped = img[top:top + ch, left:left + cw]
        zoom_tuple = (zoom_factor, zoom_factor)
        
    res = scizoom(img_cropped, zoom_tuple, order=1)
    
    trim_top = (res.shape[0] - h) // 2
    trim_left = (res.shape[1] - w) // 2
    return res[trim_top:trim_top + h, trim_left:trim_left + w]

def cv2_motion_blur(img, radius, sigma, angle):
    # Modern replacement for Wand-based motion blur using OpenCV
    size = int(2 * radius + 1)
    kernel = np.zeros((size, size))
    center = radius
    kernel[int(center), :] = 1.0
    
    # Rotate the kernel
    M = cv2.getRotationMatrix2D((center, center), angle, 1)
    kernel = cv2.warpAffine(kernel, M, (size, size))
    kernel /= np.sum(kernel)
    
    return cv2.filter2D(img, -1, kernel)

# /////////////// Corruptions ///////////////

def gaussian_noise(x, severity=1):
    c = [.08, .12, 0.18, 0.26, 0.38][severity - 1]
    x = np.array(x) / 255.
    return np.clip(x + np.random.normal(size=x.shape, scale=c), 0, 1) * 255

def shot_noise(x, severity=1):
    c = [60, 25, 12, 5, 3][severity - 1]
    x = np.array(x) / 255.
    return np.clip(np.random.poisson(x * c) / float(c), 0, 1) * 255

def impulse_noise(x, severity=1):
    c = [.03, .06, .09, 0.17, 0.27][severity - 1]
    x = random_noise(np.array(x) / 255., mode='s&p', amount=c)
    return np.clip(x, 0, 1) * 255

def speckle_noise(x, severity=1):
    c = [.15, .2, 0.35, 0.45, 0.6][severity - 1]
    x = np.array(x) / 255.
    return np.clip(x + x * np.random.normal(size=x.shape, scale=c), 0, 1) * 255

def gaussian_blur(x, severity=1):
    c = [1, 2, 3, 4, 6][severity - 1]
    x = gaussian(np.array(x) / 255., sigma=c, channel_axis=-1)
    return np.clip(x, 0, 1) * 255

def glass_blur(x, severity=1):
    # sigma, max_delta, iterations
    c = [(0.7, 1, 2), (0.9, 2, 1), (1, 2, 3), (1.1, 3, 2), (1.5, 4, 2)][severity - 1]
    x = np.uint8(gaussian(np.array(x) / 255., sigma=c[0], channel_axis=-1) * 255)
    h, w = x.shape[:2]

    for i in range(c[2]):
        # Optimized: pre-generate all random shifts for the entire image
        dxs = np.random.randint(-c[1], c[1], size=(h, w))
        dys = np.random.randint(-c[1], c[1], size=(h, w))
        
        for row in range(c[1], h - c[1]):
            for col in range(c[1], w - c[1]):
                row_prime, col_prime = row + dys[row, col], col + dxs[row, col]
                # Swap pixels
                tmp = x[row, col].copy()
                x[row, col] = x[row_prime, col_prime]
                x[row_prime, col_prime] = tmp
    return np.clip(gaussian(x / 255., sigma=c[0], channel_axis=-1), 0, 1) * 255

def defocus_blur(x, severity=1):
    c = [(3, 0.1), (4, 0.5), (6, 0.5), (8, 0.5), (10, 0.5)][severity - 1]
    x = np.array(x) / 255.
    kernel = disk(radius=c[0], alias_blur=c[1])
    res = cv2.filter2D(x, -1, kernel)
    return np.clip(res, 0, 1) * 255

def motion_blur(x, severity=1):
    c = [(10, 3), (15, 5), (15, 8), (15, 12), (20, 15)][severity - 1]
    x = np.array(x) / 255.
    angle = np.random.uniform(-45, 45)
    res = cv2_motion_blur(x, radius=c[0], sigma=c[1], angle=angle)
    return np.clip(res, 0, 1) * 255

def zoom_blur(x, severity=1):
    c = [np.arange(1, 1.11, 0.01),
         np.arange(1, 1.16, 0.01),
         np.arange(1, 1.21, 0.02),
         np.arange(1, 1.26, 0.02),
         np.arange(1, 1.31, 0.03)][severity - 1]
    x = (np.array(x) / 255.).astype(np.float32)
    out = np.zeros_like(x)
    for zoom_factor in c:
        out += clipped_zoom(x, zoom_factor)
    x = (x + out) / (len(c) + 1)
    return np.clip(x, 0, 1) * 255

def fog(x, severity=1):
    c = [(1.5, 2), (2., 2), (2.5, 1.7), (2.5, 1.5), (3., 1.4)][severity - 1]
    x = np.array(x) / 255.
    h, w = x.shape[:2]
    max_val = x.max()
    # Ensure plasma_fractal covers the image size
    pf_size = 1
    while pf_size < max(h, w): pf_size *= 2
    x += c[0] * plasma_fractal(mapsize=pf_size)[:h, :w][..., np.newaxis]
    return np.clip(x * max_val / (max_val + c[0]), 0, 1) * 255

def frost(x, severity=1):
    c = [(1, 0.4), (0.8, 0.6), (0.7, 0.7), (0.65, 0.7), (0.6, 0.75)][severity - 1]
    idx = np.random.randint(1, 7)
    ext = 'png' if idx <= 3 else 'jpg'
    
    try:
        # Modern way to access package resources
        resource_path = resources.files('corrupt_tta.assets.frost').joinpath(f'frost{idx}.{ext}')
        with resources.as_file(resource_path) as path:
            frost_img = cv2.imread(str(path))
    except (ImportError, AttributeError, FileNotFoundError):
        # Fallback for older Python versions or local testing
        asset_path = os.path.join(os.path.dirname(__file__), 'assets', 'frost', f'frost{idx}.{ext}')
        frost_img = cv2.imread(asset_path)
        
    if frost_img is None:
        return np.array(x) # Fallback if asset missing
        
    h, w = np.array(x).shape[:2]
    x_start = np.random.randint(0, frost_img.shape[0] - h)
    y_start = np.random.randint(0, frost_img.shape[1] - w)
    frost_img = frost_img[x_start:x_start + h, y_start:y_start + w][..., [2, 1, 0]]
    return np.clip(c[0] * np.array(x) + c[1] * frost_img, 0, 255)

def snow(x, severity=1):
    c = [(0.1, 0.3, 3, 0.5, 10, 4, 0.8),
         (0.2, 0.3, 2, 0.5, 12, 4, 0.7),
         (0.55, 0.3, 4, 0.9, 12, 8, 0.7),
         (0.55, 0.3, 4.5, 0.85, 12, 8, 0.65),
         (0.55, 0.3, 2.5, 0.85, 12, 12, 0.55)][severity - 1]
    x = np.array(x, dtype=np.float32) / 255.
    h, w = x.shape[:2]
    snow_layer = np.random.normal(size=x.shape[:2], loc=c[0], scale=c[1])
    snow_layer = clipped_zoom(snow_layer[..., np.newaxis], c[2])
    snow_layer[snow_layer < c[3]] = 0
    
    angle = np.random.uniform(-135, -45)
    snow_layer = cv2_motion_blur(snow_layer, radius=c[4], sigma=c[5], angle=angle)
    snow_layer = np.clip(snow_layer, 0, 1)[..., np.newaxis]
    
    gray = cv2.cvtColor(x, cv2.COLOR_RGB2GRAY).reshape(h, w, 1)
    x = c[6] * x + (1 - c[6]) * np.maximum(x, gray * 1.5 + 0.5)
    return np.clip(x + snow_layer + np.rot90(snow_layer, k=2), 0, 1) * 255

def contrast(x, severity=1):
    c = [0.4, .3, .2, .1, .05][severity - 1]
    x = np.array(x) / 255.
    means = np.mean(x, axis=(0, 1), keepdims=True)
    return np.clip((x - means) * c + means, 0, 1) * 255

def brightness(x, severity=1):
    c = [.1, .2, .3, .4, .5][severity - 1]
    x = np.array(x, dtype=np.float32) / 255.
    # Optimized: Use OpenCV for much faster color space conversion
    x = cv2.cvtColor(x, cv2.COLOR_RGB2HSV)
    x[:, :, 2] = np.clip(x[:, :, 2] + c, 0, 1)
    x = cv2.cvtColor(x, cv2.COLOR_HSV2RGB)
    return np.clip(x, 0, 1) * 255

def saturate(x, severity=1):
    c = [(0.3, 0), (0.1, 0), (2, 0), (5, 0.1), (20, 0.2)][severity - 1]
    x = np.array(x, dtype=np.float32) / 255.
    # Optimized: Use OpenCV for much faster color space conversion
    x = cv2.cvtColor(x, cv2.COLOR_RGB2HSV)
    x[:, :, 1] = np.clip(x[:, :, 1] * c[0] + c[1], 0, 1)
    x = cv2.cvtColor(x, cv2.COLOR_HSV2RGB)
    return np.clip(x, 0, 1) * 255

def jpeg_compression(x, severity=1):
    c = [25, 18, 15, 10, 7][severity - 1]
    img = PILImage.fromarray(np.uint8(x))
    from io import BytesIO
    out = BytesIO()
    img.save(out, 'JPEG', quality=c)
    return np.array(PILImage.open(out))

def pixelate(x, severity=1):
    c = [0.6, 0.5, 0.4, 0.3, 0.25][severity - 1]
    h, w = np.array(x).shape[:2]
    img = PILImage.fromarray(np.uint8(x))
    img = img.resize((int(w * c), int(h * c)), PILImage.BOX)
    img = img.resize((w, h), PILImage.BOX)
    return np.array(img)

def elastic_transform(image, severity=1):
    c = [(224 * 2, 224 * 0.7, 224 * 0.1),
         (224 * 2, 224 * 0.08, 224 * 0.2),
         (224 * 0.05, 224 * 0.01, 224 * 0.02),
         (224 * 0.07, 224 * 0.01, 224 * 0.02),
         (224 * 0.12, 224 * 0.01, 224 * 0.02)][severity - 1]
    image = np.array(image, dtype=np.float32) / 255.
    h, w = image.shape[:2]
    
    # random affine
    center_square = np.float32((h, w)) // 2
    square_size = min((h, w)) // 3
    pts1 = np.float32([center_square + square_size,
                       [center_square[0] + square_size, center_square[1] - square_size],
                       center_square - square_size])
    pts2 = pts1 + np.random.uniform(-c[2], c[2], size=pts1.shape).astype(np.float32)
    M = cv2.getAffineTransform(pts1, pts2)
    image = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT_101)
    
    dx = (gaussian(np.random.uniform(-1, 1, size=(h, w)),
                   c[1], mode='reflect', truncate=3) * c[0]).astype(np.float32)
    dy = (gaussian(np.random.uniform(-1, 1, size=(h, w)),
                   c[1], mode='reflect', truncate=3) * c[0]).astype(np.float32)
    
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))
    
    res = np.zeros_like(image)
    for i in range(image.shape[2]):
        res[..., i] = map_coordinates(image[..., i], indices, order=1, mode='reflect').reshape((h, w))
    
    return np.clip(res, 0, 1) * 255
