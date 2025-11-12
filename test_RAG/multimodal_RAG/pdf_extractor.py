import os
from unstructured.partition.pdf import partition_pdf
from langchain_text_splitters import CharacterTextSplitter

def extract_pdf_elements(path, fname):
    return partition_pdf(
        filename=os.path.join(path, fname),
        extract_images_in_pdf=True,
        infer_table_structure=True,
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        image_output_dir_path=path,
    )

def categorize_elements(raw_elements):
    texts, tables = [], []
    for el in raw_elements:
        if "Table" in str(type(el)):
            tables.append(str(el))
        elif "CompositeElement" in str(type(el)):
            texts.append(str(el))
    return texts, tables

def split_texts(texts, chunk_size=4000):
    splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=chunk_size, chunk_overlap=0)
    joined_texts = " ".join(texts)
    return splitter.split_text(joined_texts)