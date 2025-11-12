"""유틸리티 함수"""

import base64
import io
from PIL import Image

def base64_to_image(base64_str: str):
    """base64 문자열을 PIL Image로 변환"""
    img_data = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(img_data))

def format_timestamp(seconds: float) -> str:
    """초를 HH:MM:SS 형식으로 변환"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"