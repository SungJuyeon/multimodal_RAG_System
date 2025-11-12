import os
import base64
import torch
import clip
from PIL import Image

device = "cpu"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

model, preprocess = clip.load("ViT-B/32", device=device)

def generate_clip_embeddings(image_folder):
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(".jpg")]
    base64_list, summaries = [], []

    for fname in sorted(image_files):
        img_path = os.path.join(image_folder, fname)

        # 이미지 base64
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        base64_list.append(b64)

        page_info = fname.replace("figure-", "").replace(".jpg", "")
        summaries.append(f"Visual content: chart, table, or diagram extracted from document (identifier: {page_info})")

    print(f"총 {len(image_files)}개의 이미지 처리 완료")
    return base64_list, summaries