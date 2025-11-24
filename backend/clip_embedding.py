import os, base64
from PIL import Image
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI

_clip_model = None

def get_clip_model():
    global _clip_model
    if _clip_model is None:
        print("📦 CLIP 모델 로딩 중...")
        _clip_model = SentenceTransformer("clip-ViT-B-32")
    return _clip_model

def get_chat_model():
    return ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

def generate_clip_embeddings(image_folder):
    """CLIP 임베딩 + GPT-4o 요약 + 원본 경로"""
    if not os.path.exists(image_folder):
        return [], [], []

    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    image_files = [f for f in sorted(os.listdir(image_folder)) if f.lower().endswith(image_extensions)]
    if not image_files:
        return [], [], []

    clip_model = get_clip_model()
    chat_model = get_chat_model()

    clip_embeddings, summaries, paths = [], [], []
    prompt = "Summarize this image for retrieval. Provide concise summary for semantic search."

    for fname in image_files:
        img_path = os.path.join(image_folder, fname)
        try:
            # CLIP 임베딩
            img = Image.open(img_path).convert("RGB")
            embedding = clip_model.encode(img)
            clip_embeddings.append(embedding.tolist())
            paths.append(img_path)

            # base64 인코딩
            with open(img_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")

            # GPT-4o 요약
            res = chat_model.invoke([
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                    ]
                }
            ])
            summaries.append(res.content if hasattr(res, "content") else str(res))

            print(f"  ✓ {fname} 처리 완료")
        except Exception as e:
            print(f"  ❌ {fname} 처리 실패: {e}")
            continue

    return clip_embeddings, summaries
