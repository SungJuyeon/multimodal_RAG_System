import os
from unstructured.partition.pdf import partition_pdf
from langchain_text_splitters import CharacterTextSplitter

def extract_pdf_elements(path, fname):
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = current_file_dir  # 현재 디렉토리가 backend
    figure_path = os.path.join(backend_dir, "figures")
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
        extract_image_block_types=["Image", "Table"],  # 이미지 타입 명시
        extract_image_block_to_payload=False,  # 파일로 저장
    )
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