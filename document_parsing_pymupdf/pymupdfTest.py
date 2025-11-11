from langchain_community.document_loaders import PyMuPDFLoader
import fitz
import pandas as pd
import os

pdf_path = './신세계.pdf'
output_path = './신세계.txt'
base_image_dir = './images'

loader = PyMuPDFLoader(pdf_path)
docs = fitz.open(pdf_path)

pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]  # PDF 파일 이름(확장자 제거)
image_output_dir = os.path.join(base_image_dir, pdf_name)
os.makedirs(image_output_dir, exist_ok=True)


with open(output_path, 'w', encoding='utf-8') as f:
    for i, page in enumerate(docs):
        f.write(f"--- Page {i} ---\n")
        
        # 1. 텍스트 추출
        text = page.get_text("text")
        if text.strip():
            f.write(text + "\n")
        else:
            f.write("(텍스트 없음)\n")

        # 2. 표 추출
        try:
            tables = page.find_tables()
            if tables.tables:
                for t_idx, table in enumerate(tables.tables):
                    df = table.to_pandas()
                    f.write(f"페이지 {i + 1} - 표 {t_idx + 1}:")
                    f.write(df.to_markdown(index=False))
        except Exception as e:
            f.write(f"Error processing tables on page {i + 1}: {e}")

        # 3. 이미지 추출
        try: 
            image_list = page.get_images(full=True)
            if image_list:
                f.write(f"\n페이지 {i + 1} - 이미지 {len(image_list)}개 추출됨:\n")
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = docs.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_filename = f"page_{i + 1}_img_{img_index + 1}.{image_ext}"
                    image_path = os.path.join(image_output_dir, image_filename)
                    
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    f.write(f"이미지 저장됨: {image_filename}\n")
            else:
                f.write(f"\n페이지 {i + 1} - 이미지 없음\n")
        except Exception as e:
            f.write(f"Error processing page {i + 1}: {e}\n")

docs.close()