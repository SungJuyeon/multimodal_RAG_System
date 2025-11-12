from unstructured.partition.pdf import partition_pdf
import os
import shutil

pdf_path = "../input/신세계.pdf"
output_dir = "./unstructured_output"
os.makedirs(output_dir, exist_ok=True)

# PDF 문서명 (확장자 제거)
pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

elements = partition_pdf(
    filename=pdf_path,
    strategy="hi_res",               # 고해상도: 텍스트 + 이미지 + 표 모두 인식
    infer_table_structure=True,      # 표 구조 추론
    extract_images_in_pdf=True,      # 이미지 추출
    extract_image_block_types=["Image"],
    image_output_dir=output_dir,     # 이미지 저장 폴더
)

page_img_counter = {}

text_path = os.path.join(output_dir, f"{pdf_name}_text.txt")

with open(text_path, "w", encoding="utf-8") as f:
    for e in elements:
        page_num = getattr(e.metadata, "page_number", 1)

        if e.category == "Table":
            f.write(f"\n[표 - 페이지 {page_num}]\n")
            f.write(e.text + "\n")

        elif e.category == "Image":
            page_img_counter[page_num] = page_img_counter.get(page_num, 0) + 1
            img_index = page_img_counter[page_num]

            old_img_path = getattr(e.metadata, "image_path", None)
            if old_img_path and os.path.exists(old_img_path):
                ext = os.path.splitext(old_img_path)[1].lstrip(".")
                new_filename = f"{pdf_name}_page_{page_num}_img_{img_index}.{ext}"
                new_img_path = os.path.join(output_dir, new_filename)
                
                shutil.move(old_img_path, new_img_path)

                f.write(f"\n[페이지 {page_num}]\n")
                f.write(f"이미지 경로 : {new_filename}\n")
            else:
                f.write(f"(이미지 파일 경로 없음)\n")

        else:
            f.write(e.text + "\n")