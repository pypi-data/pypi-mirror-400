def pixel_to_gray_code(
    pixel: tuple[int, int, int],
) -> tuple[int, int, int]: 
    """Converts a 24-bit RGB pixel from pure binary code to Gray Code as defined [here](https://en.wikipedia.org/wiki/Gray_code).
    
    Example:
        ```
        from pixelveil.image_utils import pixel_to_gray_code
        
        pixel = (0b1110101, 0b0011000, 0b1010111)
        pixel_gray = pixel_to_gray_code(pixel)
        
        assert pixel_gray == (0b1001111, 0b0010100, 0b1111100)
        ```
    
    Args:
        pixel (tuple[int, int, int]): The pixel.
    
    Raises:
        TypeError: If one of the channels has a value that does not satisfy `0 <= value <= 255`.
    
    Returns:
        tuple[int, int, int]: The converted pixel in Gray Code.
    """
    ...

def pixel_to_binary_code(
    pixel: tuple[int, int, int],
) -> tuple[int, int, int]: 
    """Converts a 24-bit RGB pixel from Gray Code to pure binary code as defined [here](https://en.wikipedia.org/wiki/Gray_code)
    
    Example:
        ```
        from pixelveil.image_utils import pixel_to_binary_code
        
        pixel = (0b1001111, 0b0010100, 0b1111100)
        pixel_gray = pixel_to_binary_code(pixel)
        
        assert pixel_gray == (0b1110101, 0b0011000, 0b1010111)
        ```
    
    Args:
        pixel (tuple[int, int, int]): The pixel.
    
    Raises:
        TypeError: If one of the channels has a value that does not satisfy `0 <= value <= 255`.
    
    Returns:
        tuple[int, int, int]: The converted pixel in Pure Binary Code.
    """
    ...

def image_to_gray_code(
    image_bytes: bytes,
) -> bytes: 
    """Converts an image from pure binary code to Gray Code.
    
    Applies `pixel_to_gray_code` on every pixel in the image.
    
    Example:
        ```
        from pixelveil.image_utils import image_to_gray_code

        regular_image_bytes = open("path/to/img.png", "rb").read()
        
        gray_image_bytes = image_to_gray_code(regular_image_bytes)
        ```

    Args:
        image_bytes (bytes): The image.
        
    Raises:
        ValueError: If the image bytes do not represent a valid image.

    Returns:
        bytes: The converted image in Gray Code.
    """
    ...

def image_to_binary_code(
    image_bytes: bytes,
) -> bytes: 
    """Converts an image from Gray Code to pure binary code.
    
    Applies `pixel_to_binary_code` on every pixel in the image.
    
    Example:
        ```
        from pixelveil.image_utils import image_to_binary_code

        gray_image_bytes = open("path/to/img.png", "rb").read()
        
        regular_image_bytes = image_to_binary_code(gray_image_bytes)
        ```

    Args:
        image_bytes (bytes): The image.
        
    Raises:
        ValueError: If the image bytes do not represent a valid image.

    Returns:
        bytes: The converted image in Pure Binary Code.
    """
    ...
