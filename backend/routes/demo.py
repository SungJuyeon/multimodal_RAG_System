# routes/demo.py
from fastapi import APIRouter, HTTPException
from services.file_processor import get_retriever, load_existing_rag

router = APIRouter(prefix="/demo", tags=["demo"])

@router.get("/image/{conv_id}")
async def get_demo_image(conv_id: str):
    """
    vector DB에 저장된 이미지(base64) 하나를 가져와 반환
    """
    retriever = get_retriever(conv_id)
    if not retriever:
        raise HTTPException(status_code=404, detail="RAG retriever not found")

    # retriever에서 저장된 이미지 확인
    # 예시: 첫 번째 이미지 가져오기
    try:
        # retriever.docstore에서 모든 이미지 id/key 가져오기
        all_docs = retriever.docstore.mget(list(retriever.docstore._store.keys()))
        # 이미지 문서만 필터링
        image_docs = [d for d in all_docs if isinstance(d, str) and ('iVBOR' in d or '/9j/' in d)]
        if not image_docs:
            raise HTTPException(status_code=404, detail="No images found")
        image_base64 = image_docs[0]  # 첫 번째 이미지
        return {"image_base64": image_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/demo/image/{conv_id}")
async def get_demo_image(conv_id: str):
    retriever = get_retriever(conv_id)
    if not retriever:
        # 기존 RAG 로드 시도
        retriever = load_existing_rag(conv_id)
        if not retriever:
            return {"image_base64": None, "message": "Retriever not found. 서버에 기존 RAG가 없거나 로드 실패"}

    all_docs = retriever.docstore.mget(list(retriever.docstore._store.keys()))
    image_docs = [d for d in all_docs if isinstance(d, str) and ('iVBOR' in d or '/9j/' in d)]
    if not image_docs:
        return {"image_base64": None, "message": "Vector DB에 이미지가 없습니다"}

    return {"image_base64": image_docs[0], "message": "이미지 1개 가져오기 성공"}