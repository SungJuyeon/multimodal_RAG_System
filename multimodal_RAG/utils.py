import base64
import io
from PIL import Image

def base64_to_image(base64_str):
    img_data = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(img_data))

def resize_base64_image(base64_str, size=(128, 128)):
    img = base64_to_image(base64_str)
    resized = img.resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    resized.save(buf, format=img.format)
    return base64.b64encode(buf.getvalue()).decode("utf-8")