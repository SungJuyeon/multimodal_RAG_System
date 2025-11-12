from pdf_extractor import extract_pdf_elements, categorize_elements, split_texts
from summarizer import summarize_texts, summarize_images
from vector_manager import create_vectorstore, create_multi_vector_retriever
from utils import base64_to_image
from clip_embedding import generate_clip_embeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# PDF 추출
fpath = "../input/"
fname = "cj.pdf"
figure_path = "./figures"

raw_elements = extract_pdf_elements(fpath, fname)
texts, tables = categorize_elements(raw_elements)
texts_4k_token = split_texts(texts)

# 요약 생성
text_summaries, table_summaries = summarize_texts(texts_4k_token, tables, summarize_texts_flag=True)
#img_base64_list, image_summaries = summarize_images(fpath)
img_base64_list, image_summaries = generate_clip_embeddings(figure_path)

# 벡터 저장소 생성
vectorstore = create_vectorstore()
retriever = create_multi_vector_retriever(
    vectorstore, text_summaries, texts_4k_token, table_summaries, tables, image_summaries, img_base64_list
)

# 검색 예제
query = "MongoDB, Cloudflare, Datadog 관련 EV/NTM, NTM rev growth 확인하고 싶어."
docs = retriever.invoke(query, k=10)

# 결과 확인
print(f"검색된 문서 개수: {len(docs)}")
for i, doc in enumerate(docs):
    print(f"\n=== 문서 {i+1} ===")
    print(f"타입: {type(doc)}")
    
    # base64 이미지인지 확인
    if isinstance(doc, str) and doc.startswith('iVBOR') or doc.startswith('/9j/'):
        print("이미지 발견!")
        img = base64_to_image(doc)
        img.show()
    else:
        # 텍스트 또는 테이블
        print(f"내용 미리보기: {str(doc)[:200]}...")

        print(f"검색된 문서 개수: {len(docs)}\n")

# 문서를 텍스트와 이미지로 분리
text_context = []
image_base64_list = []

for doc in docs:
    if isinstance(doc, str):
        # base64 이미지 판별
        if len(doc) > 1000 and (doc.startswith('iVBOR') or doc.startswith('/9j/') or 
                                'iVBOR' in doc[:50] or '/9j/' in doc[:50]):
            image_base64_list.append(doc)
            print(f"✓ 이미지 발견")
        else:
            text_context.append(doc)
            print(f"✓ 텍스트/테이블 발견: {doc[:100]}...")

# LLM으로 답변 생성
model = ChatOpenAI(temperature=0, model="gpt-4o-mini")

# 프롬프트 구성
context_text = "\n\n---\n\n".join(text_context)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"""다음은 검색된 문서 내용입니다:

{context_text}

질문: {query}

위 문서를 참고하여 질문에 답변해주세요. 구체적인 수치와 데이터를 포함해서 답변해주세요."""
            }
        ]
    }
]

# 이미지도 함께 전달 (있을 경우)
if image_base64_list:
    print(f"\n✓ {len(image_base64_list)}개의 이미지를 LLM에 전달합니다.\n")
    for img_b64 in image_base64_list[:3]:  # 최대 3개까지
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
        })

# 답변 생성
print("="*60)
print("AI 답변:")
print("="*60)
response = model.invoke(messages)
answer = response.content if hasattr(response, "content") else str(response)
print(answer)
print("="*60)

# 이미지 표시 (선택)
if image_base64_list:
    print(f"\n검색된 이미지 {len(image_base64_list)}개 중 첫 번째 이미지:")
    img = base64_to_image(image_base64_list[0])
    img.show()