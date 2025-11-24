"""저장된 벡터 DB에서 질의응답하는 메인 스크립트"""

from video_vectorStore import VideoVectorStore
from video_rag_generator import VideoRAGGenerator
from utils import base64_to_image

def query_video(query: str, top_k: int = 3, show_images: bool = True):
    """질의에 대한 답변 생성 및 출처 표시"""
    
    print(f"\n{'='*60}")
    print(f"질문: {query}")
    print(f"{'='*60}\n")
    
    # 1. 벡터 DB에서 검색
    print("⏳ 관련 세그먼트 검색 중...")
    vector_store = VideoVectorStore(collection_name="video_rag")
    segments = vector_store.search(query, top_k=top_k)
    
    print(f"✓ {len(segments)}개 세그먼트 발견\n")
    
    # 2. 답변 생성
    print("⏳ 답변 생성 중...")
    generator = VideoRAGGenerator()
    result = generator.generate_answer(query, segments)
    
    # 3. 결과 출력
    print(f"\n{'='*10}")
    print("답변:")
    print(f"{'='*10}")
    print(result['answer'])
    print(f"\n{'='*10}")
    print(f"📍 출처: {', '.join(result['source_timestamps'])}")
    print(f"{'='*10}\n")
    
    # 4. 관련 세그먼트 상세 정보
    print("🎬 관련 영상 세그먼트:")
    for i, seg in enumerate(segments):
        minutes = int(seg['timestamp'] // 60)
        seconds = int(seg['timestamp'] % 60)
        print(f"\n[{i+1}] {minutes:02d}:{seconds:02d}")
        print(f"  음성: {seg['audio_text'][:100]}...")
        print(f"  화면: {seg['visual_description'][:100]}...")
    
    # 5. 이미지 표시 (선택)
    if show_images and segments:
        print(f"\n첫 번째 세그먼트의 프레임을 표시합니다...")
        img = base64_to_image(segments[0]['frame_base64'])
        img.show()
    
    return result

if __name__ == "__main__":
    # 사용 예시
    queries = [
        "영상의 주요 주제는 무엇인가요?",
        "시스템의 정확도는 어떻게 되나요?"
    ]
    
    for query in queries:
        result = query_video(query, top_k=3, show_images=False)
        print("\n" + "="*60 + "\n")