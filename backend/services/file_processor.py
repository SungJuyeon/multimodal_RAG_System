import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from video_processor import VideoProcessor
from video_embedding import VideoEmbedder
from video_vectorStore import VideoVectorStore
from pdf_extractor import extract_pdf_elements, categorize_elements, split_texts
from summarizer import summarize_texts
from clip_embedding import generate_clip_embeddings
from vector_manager import create_vectorstore, create_multi_vector_retriever

# 전역 retriever 저장소
_retrievers = {}

def process_video(video_path: str, conv_id: str):
    """영상 처리 및 벡터 DB 저장"""
    
    print(f"📹 영상 처리 시작: {video_path}")
    
    # 1. 영상 처리
    processor = VideoProcessor()
    key_frames, text_segments = processor.process_video(video_path)
    
    # 2. 임베딩 생성
    embedder = VideoEmbedder()
    embeddings = embedder.create_embeddings(key_frames, text_segments)
    
    # 3. 벡터 DB 저장 (conversation별로 collection 생성)
    collection_name = f"video_conv_{conv_id}"
    vector_store = VideoVectorStore(collection_name=collection_name)
    vector_store.store_video_embeddings(conv_id, embeddings)
    
    print(f"✅ 영상 처리 완료: {len(embeddings)}개 세그먼트 저장")
    
    return {
        "segments_count": len(embeddings),
        "collection_name": collection_name
    }

def process_document(pdf_path: str, conv_id: str):
    """문서 처리 및 벡터 DB 저장 (개선 버전)"""
    
    print(f"📄 문서 처리 시작: {pdf_path}")
    
    abs_pdf_path = os.path.abspath(pdf_path)
    fpath = os.path.dirname(abs_pdf_path)
    fname = os.path.basename(abs_pdf_path)
    
    # 1. PDF 추출
    print("  → PDF 파싱 중...")
    raw_elements, figure_path = extract_pdf_elements(fpath, fname, conv_id)
    texts, tables, image_count = categorize_elements(raw_elements, figure_path)
    print(f"  → 추출 완료: {len(texts)} 텍스트, {len(tables)} 테이블, {image_count} 이미지")
    
    # 2. 텍스트 분할
    texts_4k_token = split_texts(texts)
    
    # 3. 요약 생성
    print("  → 요약 생성 중...")
    text_summaries, table_summaries = summarize_texts(
        texts_4k_token, 
        tables, 
        summarize_texts_flag=True
    )
    
    # 4. 이미지 처리
    print(f"  → 이미지 폴더 확인: {figure_path}")
    images_base64, image_summaries = generate_clip_embeddings(figure_path)
    
    # 5. 벡터 저장소 생성
    print("  → 벡터 DB 생성 중...")
    collection_name = f"doc_{conv_id}"
    vectorstore = create_vectorstore(collection_name=collection_name)
    
    retriever = create_multi_vector_retriever(
        vectorstore,
        text_summaries,
        texts_4k_token,
        table_summaries,
        tables,
        image_summaries,
        images_base64
    )
    
    _retrievers[f"doc_{conv_id}"] = retriever
    
    result = {
        "texts_count": len(texts_4k_token),
        "tables_count": len(tables),
        "images_count": len(images_base64),
        "collection_name": collection_name,
        "image_folder": figure_path
    }
    
    print(f"✅ 문서 처리 완료: {result}")
    return result

def load_existing_rag(conv_id: str):
    """이미 존재하는 vectorstore retriever를 로드하여 _retrievers에 저장"""
    try:
        from vector_manager import create_vectorstore, create_multi_vector_retriever
        collection_name = f"doc_{conv_id}"
        vectorstore = create_vectorstore(collection_name=collection_name)  # load_existing=True 옵션 사용 가능 시 적용
        # 기존 vectorstore에서 retriever 생성
        # 텍스트, 테이블, 이미지는 빈 리스트로 전달 (이미 vectorstore에 문서가 저장되어 있어야 함)
        retriever = create_multi_vector_retriever(
            vectorstore,
            text_summaries=[], texts=[],
            table_summaries=[], tables=[],
            image_summaries=[], images=[]
        )
        _retrievers[f"doc_{conv_id}"] = retriever
        print(f"✅ 기존 RAG retriever 로드 완료: {conv_id}")
        return True
    except Exception as e:
        print(f"⚠️ 기존 RAG retriever 로드 실패: {conv_id}, {e}")
        return False

def get_retriever(conv_id: str, retriever_type: str = "doc"):
    """저장된 retriever 가져오기. 없으면 기존 vectorstore 로드 시도"""
    key = f"{retriever_type}_{conv_id}"
    retriever = _retrievers.get(key)
    if retriever is None:
        loaded = load_existing_rag(conv_id)
        if loaded:
            retriever = _retrievers.get(key)
    return retriever
