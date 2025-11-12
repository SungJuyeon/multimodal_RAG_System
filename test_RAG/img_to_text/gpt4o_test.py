import base64
import os
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path):
    """이미지 파일을 base64 문자열로 인코딩"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def image_summarize_gpt4o(image_base64, prompt):
    """GPT-4o-mini를 사용해 이미지 요약 생성"""
    messages = [
        {"role": "user", 
         "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
         ]
        }
    ]
    chat = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=2048
    )
    return chat.choices[0].message.content

def generate_img_summaries_gpt4o(image_folder):
    """
    폴더 내 JPG 이미지들을 GPT-4o-mini로 요약
    """
    summaries = []
    base64_list = []

    prompt = "You are an assistant tasked with summarizing images for retrieval. "\
             "Provide a concise summary of the image that can be used for semantic search."

    for img_file in sorted(os.listdir(image_folder)):
        if img_file.lower().endswith(".jpg"):
            img_path = os.path.join(image_folder, img_file)
            img_base64 = encode_image(img_path)
            base64_list.append(img_base64)
            summary = image_summarize_gpt4o(img_base64, prompt)
            summaries.append(summary)

    return base64_list, summaries

# 예시 실행
figure_path = "../multimodal_RAG/test_figure"
img_base64_list, image_summaries = generate_img_summaries_gpt4o(figure_path)

for i, s in enumerate(image_summaries):
    print(f"{i+1}. {s}")