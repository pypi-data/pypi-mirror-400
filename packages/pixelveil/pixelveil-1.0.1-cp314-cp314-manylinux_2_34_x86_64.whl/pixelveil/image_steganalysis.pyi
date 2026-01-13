def subtract_pixels(
    pixel1: tuple[int, int, int],
    pixel2: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Subtract two 24-bit RGB pixels in each one of their channels.
    
    Example:
        ```
        from pixelveil.image_steganalysis import subtract_pixels
        p1 = (13, 80, 40)
        p2 = (240, 93, 31)
        
        subtracted = subtract_pixels(p1, p2)
        
        assert subtracted == (227, 13, 9)
        ```
    
    Args:
        pixel1 (tuple[int, int, int]): The first pixel.
        pixel2 (tuple[int, int, int]): The second pixel.
    
    Raises:
        TypeError: If one of the channels has a value that does not satisfy `0 <= value <= 255`.
    
    Returns:
        tuple[int, int, int]: The absolute value of the result of subtracting the two pixels in every channel.
    """
    ...

def xor_pixels(
    pixel1: tuple[int, int, int],
    pixel2: tuple[int, int, int],
) -> tuple[int, int, int]:
    """XOR two 24-bit RGB pixels in each one of their channels.
    
    Example:
        ```
        from pixelveil.image_steganalysis import xor_pixels
        p1 = (0b10110010, 0b11011100, 0b11010001)
        p2 = (0b00100011, 0b01110001, 0b11110001)

        xored = xor_pixels(p1, p2)

        assert xored == (0b10010001, 0b10101101, 0b00100000)
        ```
    
    Args:
        pixel1 (tuple[int, int, int]): The first pixel.
        pixel2 (tuple[int, int, int]): The second pixel.
    
    Raises:
        TypeError: If one of the channels has a value that does not satisfy `0 <= value <= 255`.
    
    Returns:
        tuple[int, int, int]: A pixel that is the two passed in pixels, XORed with each other.
    """
    ...

def subtract_images(
    image1_bytes: bytes,
    image2_bytes: bytes,
) -> bytes:
    """Subtract two 24-bit RGB images from one another.
    
    Applies the `subtract_pixels` function to each pair of pixels at the same x,y and records the result in a new 
    image of the same dimensions.
    
    Example:
        ```
        from pixelveil.image_steganalysis import subtract_images
        
        img1 = open("path/to/img1.png", "rb").read()
        img2 = open("path/to/img2.png", "rb").read()
        
        subtracted = subtract_images(img1, img2)
        ```

    Args:
        image1_bytes (bytes): The first image.
        image2_bytes (bytes): The second image.
        
    Raises:
        ValueError: If one or both of the image bytes are not valid images.
        pyo3_runtime.PanicException: If the two images are not of the same size.

    Returns:
        bytes: The file bytes of an image that every pixel at x,y is the result of applying `subtract_pixels` to the 
        corresponding pixels in the two images.
    """
    ...

def xor_images(
    image1_bytes: bytes,
    image2_bytes: bytes,
) -> bytes:
    """XOR two 24-bit RGB images from one another.
    
    Applies the `xor_pixels` function to each pair of pixels at the same x,y and records the result in a new 
    image of the same dimensions.
    
    Example:
        ```
        from pixelveil.image_steganalysis import xor_images
        
        img1 = open("path/to/img1.png", "rb").read()
        img2 = open("path/to/img2.png", "rb").read()
        
        xored = xor_images(img1, img2)
        ```

    Args:
        image1_bytes (bytes): The first image.
        image2_bytes (bytes): The second image.
        
    Raises:
        ValueError: If one or both of the image bytes are not valid images.
        pyo3_runtime.PanicException: If the two images are not of the same size.

    Returns:
        bytes: The file bytes of an image that every pixel at x,y is the result of applying `xor_pixels` to the 
        corresponding pixels in the two images.
    """
    ...

def highlight_image_difference(
    image1_bytes: bytes,
    image2_bytes: bytes,
) -> bytes:
    """Highlight each different channel in each pixel between two 24-bit RGB images.
    
    Uses the `subtract_images` function to calculate the exact difference between two images. Then, sets every 
    non-zero value to 255.
    
    Example:
        ```
        from pixelveil.image_steganalysis import highlight_image_difference
        
        img1 = open("path/to/img1.png", "rb").read()
        img2 = open("path/to/img2.png", "rb").read()
        
        highlighted = highlight_image_difference(img1, img2)
        ```

    Args:
        image1_bytes (bytes): The first image.
        image2_bytes (bytes): The second image.
        
    Raises:
        ValueError: If one or both of the image bytes are not valid images.
        pyo3_runtime.PanicException: If the two images are not of the same size.

    Returns:
        bytes: The file bytes of an image that for each different channel in a pixel between the two images, the value 
        of that channel is 255.
    """
    ...

def slice_image_bit_planes(
    image_bytes: bytes,
) -> dict[tuple[int, int], bytes]:
    """Slices a 24-bit RGB image into 24 bit planes that represent each bit plane of the image as defined 
    [here](https://en.wikipedia.org/wiki/Bit_plane).
    
    Note that:
    The bit indices are ordered from left to right. This means that the most significant bit is at index 0, and the 
    least significant one is at index 7. Every bit plane is guaranteed to be in the returned dictionary (where the bit 
    indices are 0-7 and RGB channel indices are 0-2).
    
    Example:
        ```
        from pixelveil.image_steganalysis import slice_image_bit_planes
        
        img = open("path/to/img.png", "rb").read()
        
        bit_planes_dict = slice_image_bit_planes(img)
        
        green_4 = bit_planes_dict[(1, 4)]
        red_7 = bit_planes_dict[(0, 7)]
        blue_0 = bit_planes_dict[(2, 0)]
        ```

    Args:
        image_bytes (bytes): The image.
        
    Raises:
        ValueError: If the image bytes in not a valid image.

    Returns:
        dict[tuple[int, int], bytes]: A dictionary in which each key is a tuple of the channel index (R,G,B = 0,1,2) 
        and the bit index of a bit plane. And each value is the bit plane (as an image) that corresponds to the 
        matching key.
    """
    ...
