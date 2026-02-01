"""
Utilidades para manejo óptimo de imágenes en MongoDB.
Compresión y conversión de formatos.
"""

from PIL import Image
import io
from typing import Optional, Tuple

def compress_image(image: Image.Image, max_width: int = 800, quality: int = 85) -> bytes:
    """
    Comprime una imagen para optimizar almacenamiento en MongoDB.
    
    Args:
        image: Objeto PIL Image
        max_width: Ancho máximo de la imagen
        quality: Calidad de compresión JPEG (1-100)
    
    Returns:
        Bytes de la imagen comprimida
    """
    # Redimensionar si es necesario
    if image.width > max_width:
        ratio = max_width / image.width
        new_height = int(image.height * ratio)
        image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
    
    # Guardar en formato óptimo
    output = io.BytesIO()
    
    # Convertir a RGB si tiene transparencia
    if image.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
        image = background
    
    # Guardar como JPEG con compresión
    image.save(output, format="JPEG", quality=quality, optimize=True)
    output.seek(0)
    return output.getvalue()

def get_image_metadata(image: Image.Image) -> dict:
    """Obtiene metadatos básicos de una imagen."""
    return {
        "format": image.format,
        "size": image.size,
        "width": image.width,
        "height": image.height,
        "mode": image.mode
    }

def image_to_bytes(image: Image.Image, format: str = "PNG", quality: int = 85) -> bytes:
    """
    Convierte una imagen PIL a bytes en el formato especificado.
    
    Args:
        image: Objeto PIL Image
        format: Formato destino (PNG, JPEG)
        quality: Calidad para JPEG
    
    Returns:
        Bytes de la imagen
    """
    output = io.BytesIO()
    
    if format.upper() == "JPEG" or format.upper() == "JPG":
        # Convertir a RGB si es necesario
        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
            image = background
        image.save(output, format="JPEG", quality=quality, optimize=True)
    else:
        image.save(output, format=format)
    
    output.seek(0)
    return output.getvalue()

def bytes_to_image(image_bytes: bytes) -> Image.Image:
    """Convierte bytes a objeto PIL Image."""
    return Image.open(io.BytesIO(image_bytes))
