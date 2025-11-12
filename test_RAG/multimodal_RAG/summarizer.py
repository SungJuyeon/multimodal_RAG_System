import os
import base64
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# 텍스트/테이블 요약
def summarize_texts(texts, tables, summarize_texts_flag=True):
    model = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    
    text_summaries = []
    if summarize_texts_flag:
        for t in texts:
            res = model.invoke(f"Summarize for retrieval: {t}")
            # AIMessage → 문자열 추출
            text_summaries.append(res.content if hasattr(res, "content") else str(res))
    else:
        text_summaries = texts

    table_summaries = []
    for t in tables:
        res = model.invoke(f"Summarize for retrieval: {t}")
        table_summaries.append(res.content if hasattr(res, "content") else str(res))

    return text_summaries, table_summaries


# 이미지 요약 (순수 문자열 + base64)
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def summarize_images(image_folder):
    model = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    summaries, base64_list = [], []
    prompt = "Summarize this image for retrieval. Provide concise summary for semantic search."
    
    for img_file in sorted(os.listdir(image_folder)):
        if img_file.lower().endswith(".jpg"):
            img_path = os.path.join(image_folder, img_file)
            img_base64 = encode_image(img_path)
            base64_list.append(img_base64)
            
            res = model.invoke([
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
            ])
            # AIMessage → 문자열 추출
            summaries.append(res.content if hasattr(res, "content") else str(res))
    
    return base64_list, summaries