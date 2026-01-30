import os
import PIL
from google import genai
from google.genai import types
from PIL import Image
import io


def analyze_image(image: bytes):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # Convertimos los bytes a una imagen PIL
    image_stream = io.BytesIO(image)
    img_pil = PIL.Image.open(image_stream)

    result = ""
    # async for chunk in await client.aio.models.generate_content_stream(
    for chunk in client.models.generate_content_stream(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            temperature=0,
            top_p=0.95,
            top_k=20,
        ),
        contents=[
            'What is this image about?',
            types.Part.from_bytes(data=image, mime_type="image/jpeg"),
        ],
    ):
        result += chunk.text

    return result