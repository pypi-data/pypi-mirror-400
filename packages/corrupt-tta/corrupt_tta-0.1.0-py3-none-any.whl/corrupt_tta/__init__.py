from .corruptions import (
    gaussian_noise, shot_noise, impulse_noise, speckle_noise,
    gaussian_blur, glass_blur, defocus_blur, motion_blur, zoom_blur,
    fog, frost, snow,
    contrast, brightness, saturate, jpeg_compression, pixelate, elastic_transform
)

corruption_tuple = (
    gaussian_noise, shot_noise, impulse_noise, speckle_noise,
    gaussian_blur, glass_blur, defocus_blur, motion_blur, zoom_blur,
    fog, frost, snow,
    contrast, brightness, saturate, jpeg_compression, pixelate, elastic_transform
)

corruption_dict = {corr_func.__name__: corr_func for corr_func in corruption_tuple}

def corrupt(x, severity=1, corruption_name=None, corruption_number=-1):
    """
    Corrupts an image with a specified corruption and severity.
    
    :param x: image to corrupt; a numpy array in [0, 255]
    :param severity: strength with which to corrupt x; an integer in [1, 5]
    :param corruption_name: specifies which corruption function to call
    :param corruption_number: index of the corruption in corruption_tuple
    :return: corrupted image as a numpy array
    """
    if corruption_name is not None:
        return corruption_dict[corruption_name](x, severity)
    elif corruption_number != -1:
        return corruption_tuple[corruption_number](x, severity)
    else:
        raise ValueError("Either corruption_name or corruption_number must be specified.")

__version__ = "0.1.0"
