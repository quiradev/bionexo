import os
import google.generativeai as genai
from PIL import Image
import io

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_image(image_file):
    # Convertir a PIL Image
    image = Image.open(io.BytesIO(image_file.read()))
    model = genai.GenerativeModel("gemini-1.0-pro-vision")
    prompt = "Analiza esta imagen de una receta y lista los alimentos con posibles cantidades."
    response = model.generate_content([prompt, image])
    return response.text