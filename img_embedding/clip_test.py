import os
import base64
import torch
import clip
from PIL import Image
import numpy as np
import faiss

# CPU 전용 설정
device = "cpu"
os.environ["OMP_NUM_THREADS"] = "1"  # OpenMP 스레드 수 제한
os.environ["MKL_NUM_THREADS"] = "1"  # MKL 스레드 제한
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # 중복 libomp 허용

# CLIP 모델 로드
model, preprocess = clip.load("ViT-B/32", device=device)

# 이미지 디렉토리 설정
image_folder = "../multimodal_RAG_ipynb/figures"  # JPG 이미지들이 있는 폴더
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(".jpg")]

# 이미지 임베딩 계산
image_embeddings = []
image_names = []

for fname in image_files:
    img_path = os.path.join(image_folder, fname)
    image = preprocess(Image.open(img_path)).unsqueeze(0).to(device)  # 1x3x224x224
    with torch.no_grad():
        emb = model.encode_image(image)
    emb = emb.cpu().numpy()
    image_embeddings.append(emb)
    image_names.append(fname)

# FAISS용 배열로 변환
emb_matrix = np.vstack(image_embeddings).astype("float32")

# FAISS 인덱스 생성 (CPU)
dimension = emb_matrix.shape[1]
index = faiss.IndexFlatL2(dimension)  # L2 거리 기준
index.add(emb_matrix)

print(f"총 {index.ntotal}개의 이미지 임베딩이 FAISS에 추가되었습니다.")

query_img_path = os.path.join(image_folder, image_files[0])
query_image = preprocess(Image.open(query_img_path)).unsqueeze(0).to(device)
with torch.no_grad():
    query_emb = model.encode_image(query_image).cpu().numpy().astype("float32")

k = 3  # 상위 3개 유사 이미지 검색
D, I = index.search(query_emb, k)

print("Query 이미지:", image_files[0])
print("Top-k 유사 이미지:")
for idx in I[0]:
    print(" ", image_names[idx], "거리:", D[0][list(I[0]).index(idx)])