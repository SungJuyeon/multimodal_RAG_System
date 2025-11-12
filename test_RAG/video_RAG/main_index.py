"""영상을 벡터 DB에 저장하는 메인 스크립트"""

from video_processor import VideoProcessor
from video_embedding import VideoEmbedder
from video_vectorStore import VideoVectorStore
import os

def index_video(video_path: str, video_id: str = None):
    """영상을 처리하여 벡터 DB에 저장"""
    
    # 절대 경로로 변환
    abs_video_path = os.path.abspath(video_path)
    
    # 파일 존재 확인
    if not os.path.exists(abs_video_path):
        print(f"❌ 영상 파일을 찾을 수 없습니다!")
        print(f"입력한 경로: {video_path}")
        print(f"절대 경로: {abs_video_path}")
        print(f"현재 작업 디렉토리: {os.getcwd()}")
        
        # input 폴더 확인
        input_dir = os.path.join(os.getcwd(), "input")
        if os.path.exists(input_dir):
            print(f"\ninput 폴더의 파일:")
            for file in os.listdir(input_dir):
                file_path = os.path.join(input_dir, file)
                file_size = os.path.getsize(file_path) / (1024*1024)  # MB
                print(f"  - {file} ({file_size:.2f} MB)")
        else:
            print(f"\n❌ input 폴더가 존재하지 않습니다")
        
        return
    
    # 파일 정보 출력
    file_size = os.path.getsize(abs_video_path) / (1024*1024)  # MB
    print(f"✅ 영상 파일 확인: {abs_video_path}")
    print(f"파일 크기: {file_size:.2f} MB\n")
    
    # video_id가 없으면 파일명 사용
    if video_id is None:
        video_id = os.path.splitext(os.path.basename(video_path))[0]
    
    # 1. 영상 처리
    processor = VideoProcessor()
    key_frames, text_segments = processor.process_video(video_path)
    
    # 2. 임베딩 생성
    embedder = VideoEmbedder()
    embeddings = embedder.create_embeddings(key_frames, text_segments)
    
    # 3. 벡터 DB 저장
    vector_store = VideoVectorStore(collection_name="video_rag")
    vector_store.store_video_embeddings(video_id, embeddings)
    
    print(f"\n{'='*60}")
    print(f"✅ 영상 인덱싱 완료!")
    print(f"Video ID: {video_id}")
    print(f"총 {len(embeddings)}개 세그먼트 저장됨")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    # 사용 예시
    video_path = "./input/testVideo.mp4"
    index_video(video_path)