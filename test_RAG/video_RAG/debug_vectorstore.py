# diagnose_db.py - 상세 진단

import os
import chromadb

def diagnose():
    """벡터DB 상세 진단"""
    
    db_path = "./video_rag"
    
    print("="*60)
    print("벡터DB 진단 시작")
    print("="*60 + "\n")
    
    # 1. 파일 시스템 확인
    print("[1단계] 파일 시스템 확인")
    print(f"DB 경로: {db_path}")
    print(f"경로 존재: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        files = os.listdir(db_path)
        print(f"폴더 내 파일:")
        for f in files:
            size = os.path.getsize(os.path.join(db_path, f))
            print(f"  - {f} ({size} bytes)")
    print()
    
    # 2. Chroma DB 내부 확인
    print("[2단계] Chroma DB 내부 확인")
    try:
        client = chromadb.PersistentClient(path=db_path)
        collections = client.list_collections()
        
        print(f"컬렉션 개수: {len(collections)}\n")
        
        for col in collections:
            print(f"컬렉션 이름: {col.name}")
            print(f"  - 문서 개수: {col.count()}")
            print(f"  - 메타데이터: {col.metadata}")
            
            # 컬렉션 내부 데이터 직접 확인
            try:
                all_items = col.get()
                print(f"  - IDs: {len(all_items.get('ids', []))}개")
                print(f"  - Documents: {len(all_items.get('documents', []))}개")
                print(f"  - Embeddings: {len(all_items.get('embeddings', []))}개")
                
                if all_items.get('documents'):
                    print(f"  - 첫 번째 문서: {all_items['documents'][0][:100]}...")
                else:
                    print(f"  ⚠️ 문서 내용이 비어있습니다!")
            
            except Exception as e:
                print(f"  ❌ 내부 데이터 확인 실패: {e}")
            
            print()
    
    except Exception as e:
        print(f"❌ Chroma DB 확인 실패: {e}")
    
    print("="*60)

if __name__ == "__main__":
    diagnose()
