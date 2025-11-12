from typing import List, Dict
import base64
import cv2
from langchain_openai import ChatOpenAI

class VideoEmbedder:
    def __init__(self):
        self.model = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    
    def frame_to_base64(self, frame) -> str:
        """OpenCV 프레임을 base64로 인코딩"""
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')
    
    def find_text_at_timestamp(self, text_segments: List[Dict], timestamp: float) -> str:
        """특정 타임스탬프에 해당하는 텍스트 찾기"""
        for segment in text_segments:
            if segment['start'] <= timestamp <= segment['end']:
                return segment['text']
        
        # 가장 가까운 텍스트 찾기
        closest_segment = min(text_segments, 
                            key=lambda s: abs(s['start'] - timestamp))
        return closest_segment['text']
    
    def analyze_frame_with_gpt4(self, frame_base64: str) -> str:
        """GPT-4o-mini로 프레임 내용 분석"""
        prompt = """이 영상 프레임을 매우 구체적으로 분석해주세요:

                    **필수 포함 사항:**
                    1. 화면에 보이는 텍스트나 숫자 (정확히 읽어주세요)
                    2. 차트, 그래프, 표가 있다면 구체적인 데이터 값
                    3. 사람이 있다면 몇 명인지, 무엇을 하고 있는지
                    4. 주요 객체나 배경
                    5. 전체적인 분위기나 맥락

                    **형식:** 
                    - 한 문장당 하나의 구체적인 정보
                    - 애매한 표현(~인 것 같다) 대신 명확한 서술
                    - 숫자나 텍스트는 정확히 기록

                    예시: "화면 왼쪽에 'Revenue Growth 2024' 제목의 막대 그래프, Q1: 25%, Q2: 32%, Q3: 28%의 데이터가 표시됨"
                """
        
        try:
            response = self.model.invoke([
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{frame_base64}"}
                        }
                    ]
                }
            ])
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            return f"프레임 분석 실패: {str(e)}"
    
    def create_embeddings(self, key_frames: List[Dict], text_segments: List[Dict]) -> List[Dict]:
        """프레임과 텍스트를 결합하여 임베딩 데이터 생성"""
        embeddings = []
        
        print(f"\n⏳ 임베딩 생성 중... ({len(key_frames)}개 프레임)")
        
        for i, frame_data in enumerate(key_frames):
            try:
                timestamp = frame_data['timestamp']
                frame = frame_data['frame']
                
                # 프레임을 base64로 인코딩
                frame_base64 = self.frame_to_base64(frame)
                
                # 해당 시간의 음성 텍스트 찾기
                audio_text = self.find_text_at_timestamp(text_segments, timestamp)
                
                # GPT-4o-mini로 프레임 내용 분석
                visual_description = self.analyze_frame_with_gpt4(frame_base64)
                
                # 검색용 요약 생성 (오디오 + 시각적 설명)
                summary = f"""[{self._format_timestamp(timestamp)}]
                            음성: {audio_text}
                            화면: {visual_description}"""
                
                # 데이터 유효성 확인
                if not summary.strip():
                    print(f"⚠️  경고: {i}번째 프레임의 요약이 비어있음")
                    continue
                
                embeddings.append({
                    'timestamp': timestamp,
                    'summary': summary,
                    'audio_text': audio_text,
                    'visual_description': visual_description,
                    'frame_base64': frame_base64
                })
                
                print(f"  ✓ {i+1}/{len(key_frames)} - {self._format_timestamp(timestamp)}")
                
            except Exception as e:
                print(f"  ❌ {i}번째 프레임 처리 실패: {e}")
                continue
        
        print(f"✓ 임베딩 생성 완료! (총 {len(embeddings)}개)\n")
        return embeddings
    
    def _format_timestamp(self, seconds: float) -> str:
        """초를 MM:SS 형식으로 변환"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"