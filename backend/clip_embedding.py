import os
import base64
from PIL import Image

def generate_clip_embeddings(image_folder):
    """이미지 임베딩 생성"""
    if image_folder is None:
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = current_file_dir  # 현재 디렉토리가 backend
        image_folder = os.path.join(backend_dir, "figures")

    abs_image_folder = os.path.abspath(image_folder)
    print(f"📍 이미지 폴더 경로: {abs_image_folder}")

    if not os.path.exists(abs_image_folder):
        print(f"⚠️ 이미지 폴더가 존재하지 않습니다: {abs_image_folder}")
        return [], []
    
    # 다양한 이미지 확장자 지원
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    image_files = [
        f for f in os.listdir(image_folder) 
        if f.lower().endswith(image_extensions)
    ]
    
    if not image_files:
        print(f"⚠️ {image_folder}에서 이미지를 찾을 수 없습니다.")
        folder_contents = os.listdir(abs_image_folder) if os.path.exists(abs_image_folder) else []
        print(f"   폴더 내용: {folder_contents}")
        return [], []
    print(f"📸 발견된 이미지 파일: {image_files}")
    base64_list, summaries = [], []

    for fname in sorted(image_files):
        img_path = os.path.join(image_folder, fname)
        
        try:
            # 이미지 유효성 검사
            with Image.open(img_path) as img:
                # RGB로 변환 (RGBA, grayscale 등 처리)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # base64 인코딩
                with open(img_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                base64_list.append(b64)
                
                # 메타데이터 추출
                page_info = fname.replace("figure-", "").replace("-", "_")
                for ext in image_extensions:
                    page_info = page_info.replace(ext, "")
                
                summaries.append(
                    f"Visual content from page {page_info}: "
                    f"chart, diagram, or illustration (size: {img.size})"
                )
                
        except Exception as e:
            print(f"❌ 이미지 처리 실패 ({fname}): {e}")
            continue

    print(f"✅ {len(image_files)}개 이미지 중 {len(base64_list)}개 처리 완료")
    return base64_list, summaries