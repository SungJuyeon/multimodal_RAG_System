from video_vectorStore import VideoVectorStore

conv_id = "video_conv_1763127029420"

store = VideoVectorStore(collection_name=conv_id)
docs = store.get_all_documents()

print(f"\n📦 저장된 문서 수: {len(docs)}개\n")

for i, doc in enumerate(docs):
    print(f"---- 문서 {i+1} ----")
    print(f"⏱ timestamp: {doc.metadata.get('timestamp')}")
    print(f"🗣 audio_text: {doc.metadata.get('audio_text')}")
    print(f"🎞 visual_description: {doc.metadata.get('visual_description')[:80]}...")
    print(f"🖼 frame_base64 존재?: {'frame_base64' in doc.metadata}")
    print(f"📄 summary 일부: {doc.page_content[:120]}...")
    print("-------------------------\n")

# from chromadb import PersistentClient
# import os

# def list_all_conv_ids(persist_dir="./video_rag"):
#     print(f"\n📁 검색 위치: {os.path.abspath(persist_dir)}")

#     if not os.path.exists(persist_dir):
#         print("❌ video_rag 디렉토리가 없습니다.")
#         return

#     try:
#         client = PersistentClient(path=persist_dir)
#         collections = client.list_collections()

#         if not collections:
#             print("❌ 저장된 컬렉션 없음")
#             return

#         print(f"\n📦 저장된 conv_id / 컬렉션 목록 ({len(collections)}개):\n")
#         for col in collections:
#             print(f" - {col.name}")

#         print("\n✔ conv_id 출력 완료!")

#     except Exception as e:
#         print(f"❌ 오류 발생: {e}")

# # 실행
# list_all_conv_ids()