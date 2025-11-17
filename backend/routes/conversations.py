from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import os
import shutil
from services.file_processor import get_retriever, process_document, process_video
from services.rag_service import query_rag_system

router = APIRouter(prefix="/conversations", tags=["conversations"])

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    video_sources: List[dict] = []
    images: List[str] = []

# 임시 DB
UPLOAD_DIR = "./uploads"
conversations_data = {}

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{conv_id}/upload")
async def upload_file(conv_id: str, file: UploadFile = File(...)):
    """파일 업로드 및 처리"""
    
    # 대화 초기화
    if conv_id not in conversations_data:
        conversations_data[conv_id] = {
            "files": [],
            "rag_ready": False
        }
    
    # 파일 저장
    file_ext = os.path.splitext(file.filename)[1].lower()
    file_path = os.path.join(UPLOAD_DIR, f"{conv_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 파일 타입 결정
    file_type = "video" if file_ext in [".mp4", ".avi", ".mov"] else "document"
    
    file_info = {
        "id": f"{conv_id}_{len(conversations_data[conv_id]['files'])}",
        "name": file.filename,
        "type": file_type,
        "path": file_path,
        "size": round(os.path.getsize(file_path) / (1024 * 1024), 2),  # MB
        "status": "completed"
    }
    
    conversations_data[conv_id]["files"].append(file_info)
    
    return {
        "success": True,
        "file": file_info
    }

@router.post("/{conv_id}/create-rag")
async def create_rag(conv_id: str):
    """RAG 시스템 생성 (벡터 DB에 저장)"""
    
    if conv_id not in conversations_data:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")
    
    files = conversations_data[conv_id]["files"]
    
    if not files:
        raise HTTPException(status_code=400, detail="업로드된 파일이 없습니다")
    
    # 각 파일 타입별로 처리
    for file in files:
        if file["type"] == "document":
            process_document(file["path"], conv_id)
        elif file["type"] == "video":
            process_video(file["path"], conv_id)
    
    conversations_data[conv_id]["rag_ready"] = True
    
    return {
        "success": True,
        "message": "RAG 시스템 생성 완료",
        "processed_files": len(files)
    }

@router.post("/{conv_id}/query")
async def query_endpoint(conv_id: str, request: QueryRequest):
    """질의응답"""
    
    if conv_id not in conversations_data:
        # 서버 재시작 후에도 기존 RAG 접근 가능하도록 시도
        retriever = get_retriever(conv_id)
        if retriever is None:
            raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")
        # conversations_data 초기화
        conversations_data[conv_id] = {"files": [], "rag_ready": True}

    
    if not conversations_data[conv_id].get("rag_ready"):
        raise HTTPException(status_code=400, detail="RAG 시스템이 준비되지 않았습니다")
    
    # RAG 시스템으로 질의
    answer, video_sources, image_base64_list = query_rag_system(conv_id, request.query)
    
    return QueryResponse(
        answer=answer,
        video_sources=video_sources,
        images=image_base64_list[:3]
    )

@router.get("/{conv_id}/status")
async def get_status(conv_id: str):
    """대화 상태 조회"""
    
    if conv_id not in conversations_data:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")
    
    return {
        "conv_id": conv_id,
        "files_count": len(conversations_data[conv_id]["files"]),
        "rag_ready": conversations_data[conv_id]["rag_ready"],
        "files": conversations_data[conv_id]["files"]
    }

@router.delete("/{conv_id}/files/{file_id}")
async def delete_file(conv_id: str, file_id: str):
    """파일 삭제"""
    
    if conv_id not in conversations_data:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다")
    
    files = conversations_data[conv_id]["files"]
    file_to_remove = None
    
    for file in files:
        if file["id"] == file_id:
            file_to_remove = file
            break
    
    if not file_to_remove:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    # 파일 삭제
    if os.path.exists(file_to_remove["path"]):
        os.remove(file_to_remove["path"])
    
    files.remove(file_to_remove)
    conversations_data[conv_id]["rag_ready"] = False
    
    return {"success": True, "deleted_file_id": file_id}