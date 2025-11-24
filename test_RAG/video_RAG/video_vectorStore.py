# video_vectorStore.py 수정
from typing import List, Dict
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

class VideoVectorStore:
    def __init__(self, collection_name: str = "video-segments", persist_directory: str = "./video_rag"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY")),
            persist_directory=persist_directory  # 영구 저장 경로 지정
        )
    
    def store_video_embeddings(self, video_id: str, embeddings: List[Dict]):
        """영상 임베딩을 벡터 DB에 저장"""
        print(f"\n⏳ 벡터 DB 저장 중... ({len(embeddings)}개 세그먼트)")
        
        if not embeddings:
            print("❌ 저장할 임베딩이 없습니다!")
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for i, emb in enumerate(embeddings):
            doc_id = f"{video_id}_{i}_{uuid.uuid4()}"
            
            # summary가 None이 아닌지 확인
            summary = emb.get('summary', '')
            if not summary:
                print(f"⚠️  경고: {i}번째 임베딩의 summary가 비어있음")
                continue
            
            documents.append(summary)
            metadatas.append({
                'video_id': video_id,
                'timestamp': float(emb['timestamp']),
                'audio_text': emb.get('audio_text', ''),
                'visual_description': emb.get('visual_description', ''),
                'frame_base64': emb['frame_base64']
            })
            ids.append(doc_id)
        
        print(f"실제 저장할 문서: {len(documents)}개")
        
        if documents:
            # 저장 실행
            self.vectorstore.add_texts(
                texts=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            # 즉시 확인
            count = self.vectorstore._collection.count()
            print(f"✓ 벡터 DB 저장 완료! (총 {count}개 문서)")
        else:
            print("❌ 저장할 유효한 문서가 없습니다!")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """쿼리에 맞는 영상 세그먼트 검색"""
        print(f"\n⏳ '{query}' 검색 중...")
        
        # 저장된 문서 수 확인
        try:
            count = self.vectorstore._collection.count()
            print(f"현재 저장된 문서: {count}개")
            
            if count == 0:
                print("❌ 저장된 문서가 없습니다!")
                return []
        except Exception as e:
            print(f"⚠️  문서 수 확인 실패: {e}")
        
        results = self.vectorstore.similarity_search(query, k=top_k)
        
        if not results:
            print("❌ 검색 결과가 없습니다!")
            return []
        
        print(f"✓ {len(results)}개 세그먼트 발견")
        
        segments = []
        for result in results:
            segments.append({
                'timestamp': result.metadata.get('timestamp', 0),
                'audio_text': result.metadata.get('audio_text', ''),
                'visual_description': result.metadata.get('visual_description', ''),
                'frame_base64': result.metadata.get('frame_base64', ''),
                'summary': result.page_content
            })
        
        return segments