from typing import List, Dict
from langchain_openai import ChatOpenAI

class VideoRAGGenerator:
    def __init__(self):
        self.model = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    
    def generate_answer(self, query: str, segments: List[Dict]) -> Dict:
        """검색된 세그먼트를 바탕으로 답변 생성"""
        
        # 컨텍스트 구성
        context_parts = []
        for i, seg in enumerate(segments):
            timestamp_str = self._format_timestamp(seg['timestamp'])
            context_parts.append(f"""
[세그먼트 {i+1}] - {timestamp_str}
음성: {seg['audio_text']}
화면: {seg['visual_description']}
""")
        
        context = "\n".join(context_parts)
        
        # 프롬프트 구성
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""다음은 영상에서 검색된 관련 세그먼트입니다:

{context}

질문: {query}

위 정보를 바탕으로 질문에 답변해주세요. 
답변에는 반드시 해당 내용이 나오는 시간(MM:SS)을 포함하세요.
여러 세그먼트에 걸쳐 있다면 모두 언급하세요."""
                    }
                ]
            }
        ]
        
        # 이미지도 함께 전달 (최대 2개)
        for seg in segments[:2]:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{seg['frame_base64']}"}
            })
        
        # 답변 생성
        response = self.model.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)
        
        # 타임스탬프 목록
        timestamps = [self._format_timestamp(seg['timestamp']) for seg in segments]
        
        return {
            'answer': answer,
            'source_timestamps': timestamps,
            'segments': segments
        }
    
    def _format_timestamp(self, seconds: float) -> str:
        """초를 MM:SS 형식으로 변환"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
