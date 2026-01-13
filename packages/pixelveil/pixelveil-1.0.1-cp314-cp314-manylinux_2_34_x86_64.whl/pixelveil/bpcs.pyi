def embed_data(
    vessel_image_bytes: bytes,
    data: bytes,
    min_alpha: float,
    rng_key: bytes,
) -> bytes:
    """Embed data into an image using BPCS.
    
    Example:
        ```
        from pixelveil import bpcs

        rng_key = b"KEY1" * 8
        min_alpha = 0.3

        data_bytes = open("path/to/data/to/hide.txt", "rb").read()
        vessel_image_bytes = open("path/to/vessel/image.png", "rb").read()

        new_image_bytes = bpcs.embed_data(vessel_image_bytes, data_bytes, min_alpha, rng_key)
        ```

    Args:
        vessel_image_bytes (bytes): The bytes (file bytes) of the vessel image.
        data (bytes): The bytes to embed inside the vessel image.
        min_alpha (float): The BPCS minimum complexity coefficient.
        rng_key (bytes): The randomization key, used for pseudo-random selection of where to change the source image. 
            Must have a length of 32.
            
    Raises:
        ValueError: If the inputted vessel image bytes do not represent an image in a common format.
        ValueError: If the randomization key is of invalid length.
        ValueError: If there isn't enough space in the image.

    Returns:
        bytes: The file bytes of the resulting image, in a .png format.
    """
    ...

def extract_data(
    vessel_image_bytes: bytes,
    min_alpha: float,
    rng_key: bytes,
) -> bytes:
    """Extract data from an image using BPCS.
    
    Example:
        ```
        from pixelveil import bpcs

        rng_key = b"KEY1" * 8
        min_alpha = 0.3
        
        vessel_image = ... # The vessel image that was outputted from embed_data.
        
        extracted_data = bpcs.extract_data(vessel_image, min_alpha, rng_key)
        ```
    
    Args:
        vessel_image_bytes (bytes): The vessel image bytes.
        min_alpha (float): The BPCS minimum complexity coefficient.
        rng_key (bytes): The randomization key, used for pseudo-random selection of where to change the source image. 
            Must have a length of 32.
    
    Raises:
        ValueError: If the inputted vessel image bytes do not represent an image in a common format.
        ValueError: If the randomization key is of invalid length.
        ValueError: If there was an error with extracting the data. The most likely cause of this is incorrect function 
            parameters.
    
    Returns:
        bytes: The extracted data from the vessel image.
    """
    ...

def estimate_maximum_capacity(
    vessel_image_bytes: bytes,
    min_alpha: float,
) -> int:
    """Estimate how much data can be embedded in an image using BPCS and given parameters.
    
    Example:
        ```
        from pixelveil import bpcs

        min_alpha = 0.3
        vessel_image_bytes = open("path/to/vessel/image.png", "rb").read()
        
        estimated_capacity = bpcs.estimate_maximum_capacity(vessel_image_bytes, min_alpha)
        ```
    
    Args:
        vessel_image_bytes (bytes): The vessel image bytes.
        min_alpha (float): The BPCS minimum complexity coefficient.
    
    Raises:
        ValueError: If the inputted vessel image bytes do not represent an image in a common format.
    
    Returns:
        int: The amount of bytes that is estimated to be the maximum amount of data that can be embedded in the image 
        using BPCS and this library.
    """
    ...
