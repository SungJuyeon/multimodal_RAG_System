import os
import shutil
from unstructured.partition.pdf import partition_pdf
from langchain_text_splitters import CharacterTextSplitter

# 전역 retriever 저장소
_retrievers = {}

def extract_pdf_elements(path, fname, conv_id):
    # 모든 이미지를 ./figures 폴더에 저장
    figure_path = os.path.abspath("./figures")
    os.makedirs(figure_path, exist_ok=True)
    print(f"📍 이미지 저장 경로: {figure_path}")

    raw_elements = partition_pdf(
        filename=os.path.join(path, fname),
        extract_images_in_pdf=True,
        infer_table_structure=True,
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        image_output_dir_path=figure_path,
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=False,
    )
    # 추출된 이미지 파일 이름에 conv_id 붙이기
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    for f in os.listdir(figure_path):
        if f.lower().endswith(image_extensions):
            old_path = os.path.join(figure_path, f)
            new_name = f"{conv_id}_{f}"
            new_path = os.path.join(figure_path, new_name)
            # 이름이 이미 conv_id로 시작하지 않으면 변경
            if not f.startswith(f"{conv_id}_"):
                shutil.move(old_path, new_path)
                print(f"  → 이미지 이름 변경: {f} → {new_name}")

    return raw_elements, figure_path

def categorize_elements(raw_elements, figure_path=None):
    """요소를 텍스트, 테이블, 이미지로 분류"""
    texts, tables = [], []
        
    for el in raw_elements:
        el_type = str(type(el))
        
        if "Table" in el_type:
            tables.append(str(el))
        elif "CompositeElement" in el_type:
            texts.append(str(el))
    # 이미지는 파일 시스템에서 직접 확인
    image_count = 0
    if figure_path and os.path.exists(figure_path):
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        image_files = [
            f for f in os.listdir(figure_path) 
            if f.lower().endswith(image_extensions)
        ]
        image_count = len(image_files)
        print(f"📸 {figure_path}에서 {image_count}개 이미지 발견")
    
    return texts, tables, image_count


def split_texts(texts, chunk_size=4000):
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size, 
        chunk_overlap=0
    )
    joined_texts = " ".join(texts)
    return splitter.split_text(joined_texts)