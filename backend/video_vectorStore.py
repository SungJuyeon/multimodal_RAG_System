import shutil
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
        
        # 임베딩 함수 초기화
        self.embedding_function = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Chroma 버전 충돌 방지
        try:
            # Chroma 벡터 스토어 초기화
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embedding_function,
                persist_directory=persist_directory
            )
        except Exception as e:
            error_msg = str(e)
            if "no such column: collections.topic" in error_msg:
                print(f"⚠️ Chroma DB 버전 충돌 감지!")
                print(f"💡 해결: chromadb를 0.4.24로 다운그레이드하거나")
                print(f"   기존 DB를 삭제하세요: rm -rf {persist_directory}")
                
                # 자동 복구 시도 (선택사항)
                response = input("기존 DB를 삭제하고 새로 시작하시겠습니까? (y/n): ")
                if response.lower() == 'y':
                    if os.path.exists(persist_directory):
                        shutil.rmtree(persist_directory)
                        print(f"✅ {persist_directory} 삭제 완료")
                    
                    # 재시도
                    self.vectorstore = Chroma(
                        collection_name=collection_name,
                        embedding_function=self.embedding_function,
                        persist_directory=persist_directory
                    )
                else:
                    raise
            else:
                raise
    
    def store_video_embeddings(self, video_id: str, embeddings: List[Dict]):
        """영상 임베딩을 벡터 DB에 저장"""
        print(f"\n⏳ 벡터 DB 저장 중... ({len(embeddings)}개 세그먼트)")
        
        if not embeddings:
            print("❌ 저장할 임베딩이 없습니다!")
            return
        
        # Document 객체 리스트 생성
        documents = []
        
        for i, emb in enumerate(embeddings):
            # summary가 None이 아닌지 확인
            summary = emb.get('summary', '')
            if not summary or not summary.strip():
                print(f"⚠️  경고: {i}번째 임베딩의 summary가 비어있음")
                continue
            
            # Document 객체 생성
            doc = Document(
                page_content=summary,
                metadata={
                    'video_id': video_id,
                    'timestamp': float(emb.get('timestamp', 0)),
                    'audio_text': emb.get('audio_text', ''),
                    'visual_description': emb.get('visual_description', ''),
                    'frame_base64': emb.get('frame_base64', ''),
                    'doc_id': f"{video_id}_{i}_{uuid.uuid4()}"
                }
            )
            documents.append(doc)
        
        print(f"실제 저장할 문서: {len(documents)}개")
        
        if not documents:
            print("❌ 저장할 유효한 문서가 없습니다!")
            return
        
        try:
            # add_documents 메서드 사용 (Document 객체 리스트 전달)
            ids = [doc.metadata['doc_id'] for doc in documents]
            self.vectorstore.add_documents(documents=documents, ids=ids)
            
            # 저장 확인
            count = self.vectorstore._collection.count()
            print(f"✓ 벡터 DB 저장 완료! (총 {count}개 문서)")
            
            # 첫 번째 문서 확인
            if count > 0:
                test_results = self.vectorstore.similarity_search("test", k=1)
                if test_results:
                    print(f"✓ 저장 검증 성공:")
                    print(f"  - 페이지 내용 길이: {len(test_results[0].page_content)}")
                    print(f"  - 메타데이터 키: {list(test_results[0].metadata.keys())}")
                    print(f"  - timestamp: {test_results[0].metadata.get('timestamp')}")
                    print(f"  - frame_base64 존재: {'frame_base64' in test_results[0].metadata}")
        
        except Exception as e:
            print(f"❌ 벡터 DB 저장 실패: {e}")
            import traceback
            traceback.print_exc()
    
    def search(self, query: str, k: int = 3, top_k: int = None) -> List[Dict]:
        """쿼리에 맞는 영상 세그먼트 검색"""
        # top_k가 명시적으로 전달되면 우선, 아니면 k 사용
        search_k = top_k if top_k is not None else k
        
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
        
        try:
            results = self.vectorstore.similarity_search(query, k=search_k)
            
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
                    'summary': result.page_content,
                    'metadata': result.metadata,
                    'text': result.metadata.get('audio_text', '')  # rag_service에서 사용
                })
            
            return segments
        
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_all_documents(self) -> List[Document]:
        """저장된 모든 문서 조회 (디버깅용)"""
        try:
            count = self.vectorstore._collection.count()
            if count == 0:
                print("저장된 문서가 없습니다.")
                return []
            
            # 더미 쿼리로 모든 문서 가져오기
            results = self.vectorstore.similarity_search("", k=count)
            return results
        except Exception as e:
            print(f"문서 조회 실패: {e}")
            return []