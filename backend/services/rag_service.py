"""RAG 질의응답 서비스"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from langchain_openai import ChatOpenAI
from video_vectorStore import VideoVectorStore
from services.file_processor import get_retriever

def query_rag_system(conv_id: str, query: str):
    """RAG 시스템에 질의하여 답변 생성"""
    
    print(f"🔍 질의: {query}")
    
    # 1. 문서 검색
    doc_results = []
    doc_retriever = get_retriever(conv_id, "doc")
    
    if doc_retriever:
        try:
            doc_results = doc_retriever.invoke(query)
            print(f"📄 문서 검색 결과: {len(doc_results)}개")
        except Exception as e:
            print(f"📄 문서 검색 실패: {e}")
    
    # 2. 영상 검색
    video_results = []
    video_sources = []
    
    try:
        collection_name = f"video_conv_{conv_id}"
        video_store = VideoVectorStore(collection_name=collection_name)
        video_results = video_store.search(query, k=3)
        
        for result in video_results:
            metadata = result.get("metadata", {})
            timestamp = metadata.get("timestamp", 0)
            video_sources.append({
                "time": _format_timestamp(timestamp),
                "text": result.get("audio_text", result.get("text", ""))[:50] + "..."
            })
        
        print(f"🎬 영상 검색 결과: {len(video_results)}개")
    except Exception as e:
        print(f"영상 검색 실패: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 컨텍스트 구성
    text_context = []
    image_base64_list = []
    
    print(f"\n📊 문서 결과 처리 중... (총 {len(doc_results)}개)")

    for i, doc in enumerate(doc_results):
        # Document 객체 처리
        if hasattr(doc, 'page_content'):
            content = doc.page_content
        elif isinstance(doc, dict):
            content = doc.get('page_content', str(doc))
        else:
            content = str(doc)
        
        # 이미지 판별 (base64 문자열 패턴)
        # MultiVectorRetriever는 docstore에서 원본 문서를 가져오므로
        # 이미지는 매우 긴 base64 문자열로 저장되어 있음
        if len(content) > 1000:  # 이미지는 보통 매우 긺
            # base64 이미지 시작 패턴 확인
            content_start = content[:100]
            if any(pattern in content_start for pattern in ['/9j/', 'iVBOR', 'R0lGOD', 'PHN2Zy']):
                image_base64_list.append(content)
                print(f"  🖼️ 이미지 {len(image_base64_list)} 발견 (크기: {len(content)} bytes)")
            else:
                # 매우 긴데 이미지 패턴이 없으면 긴 텍스트
                text_context.append(content)
                print(f"  📝 긴 텍스트 추가 (길이: {len(content)} chars)")
        else:
            # 짧은 텍스트
            text_context.append(content)
            print(f"  📝 텍스트 {i+1} 추가 (길이: {len(content)} chars)")
    
    # 영상 텍스트도 컨텍스트에 추가
    for result in video_results:
        timestamp = result.get('timestamp', 0)
        audio_text = result.get('audio_text', '')
        visual_desc = result.get('visual_description', '')
        # 영상 컨텍스트 포맷
        video_context = f"""[영상 {_format_timestamp(timestamp)}]
                            음성: {audio_text}
                            화면: {visual_desc[:100]}..."""
        
        text_context.append(video_context)
        print(f"  🎬 영상 세그먼트 추가: [{_format_timestamp(timestamp)}]")
    
    # 4. LLM으로 답변 생성
    model = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    
    context_text = "\n\n---\n\n".join(text_context[:10])  # 최대 10개만 사용
    
    # 메시지 구성
    content_parts = [
        {
            "type": "text",
            "text": f"""다음은 검색된 문서 및 영상 내용입니다:

{context_text}

질문: {query}

위 자료를 참고하여 질문에 답변해주세요. 
- 차트나 표 이미지가 포함되어 있다면 이미지를 분석하여 구체적인 수치를 제공하세요.
- 문서에 명시된 정확한 숫자와 데이터를 사용하세요."""
        }
    ]
    
    # 이미지 추가 (최대 5개)
    for i, img_b64 in enumerate(image_base64_list[:5]):
        # base64 문자열이 이미 data URL 형식인지 확인
        if img_b64.startswith('data:image'):
            image_url = img_b64
        else:
            image_url = f"data:image/jpeg;base64,{img_b64}"
        
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": image_url}
        })
        print(f"  🖼️ LLM에 이미지 {i+1} 전달")
    
    messages = [{"role": "user", "content": content_parts}]
    
    # 답변 생성
    try:
        response = model.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)
        print(f"✅ 답변 생성 완료")
    except Exception as e:
        print(f"❌ 답변 생성 실패: {e}")
        answer = "죄송합니다. 답변 생성 중 오류가 발생했습니다."
    
    # 3개 반환: answer, video_sources, image_base64_list
    return answer, video_sources, image_base64_list


def _format_timestamp(seconds: float) -> str:
    """초를 MM:SS 형식으로 변환"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"