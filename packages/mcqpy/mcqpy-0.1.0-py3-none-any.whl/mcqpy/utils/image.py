from pathlib import Path

def check_if_url(url: str | Path) -> bool:
    """Check if a given string is a valid URL.

    Args:
        url (str): The string to check.
    Returns:
        bool: True if the string is a URL, False otherwise.
    """
    if isinstance(url, Path):
        url = str(url)

    return url.startswith('http://') or url.startswith('https://')


def get_url_image_suffix(url: str) -> bool:
    """Get the image suffix from a URL.

    Args:
        url (str): The URL of the image.
    Returns:
        str: The image suffix (e.g., '.jpg', '.png').
    """
    url = str(url)
    if '.' in url:
        return '.' + url.split('.')[-1].split('?')[0]
    return None


def download_image(url: str, save_path: str) -> None:
    """Download an image from a URL and save it to a specified path.

    Args:
        url (str): The URL of the image to download.
        save_path (str): The file path where the image will be saved.
    """
    import requests

    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    # Try to determine the suffix from the URL
    suffix = get_url_image_suffix(url)

    p = Path(save_path)
    p.parent.mkdir(parents=True, exist_ok=True)  # Create parent directories if needed
    p = p.with_suffix(suffix)

    with open(p, 'wb') as file:
        file.write(response.content)
    
    return p

def convert_image(path):
    """Convert image to PNG format using Pillow.
    
    Args:
        path: Path to the image file to convert.
    """
    from PIL import Image
    
    path = Path(path)
    img = Image.open(path)
    
    # Convert to RGB if necessary (e.g., for RGBA or other modes)
    if img.mode in ('RGBA', 'LA', 'P'):
        # Create white background for transparent images
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Save as PNG
    png_path = path.with_suffix('.png')
    img.save(png_path, 'PNG')
    
    # Remove original if different
    if png_path != path:
        path.unlink()
    
    return png_path

def check_and_download_tmp(url, tmp_name):
    if check_if_url(url):
        path = download_image(url, tmp_name)
        convert_image(path)
        return path.resolve()
    return url