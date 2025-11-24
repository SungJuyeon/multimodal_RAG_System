import uuid
from langchain_core.documents import Document
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

def create_vectorstore(collection_name="sample-rag-multi-modal"):
    return Chroma(collection_name=collection_name, embedding_function=OpenAIEmbeddings())

def create_multi_vector_retriever(vectorstore, text_summaries, texts, table_summaries, tables, image_summaries, clip_embeddings, image_paths):
    store = InMemoryStore()
    retriever = MultiVectorRetriever(vectorstore=vectorstore, docstore=store, id_key="doc_id")

    def add_docs(summaries, contents, doc_type="text", paths=None):
        ids = [str(uuid.uuid4()) for _ in contents]
        summary_docs = []
        for i, s in enumerate(summaries):
            metadata = {"doc_id": ids[i], "type": doc_type}
            if paths:
                metadata["path"] = paths[i]
            summary_docs.append(Document(page_content=s, metadata=metadata))
        retriever.vectorstore.add_documents(summary_docs)
        retriever.docstore.mset(list(zip(ids, contents)))

    if text_summaries:
        add_docs(text_summaries, texts, doc_type="text")
    if table_summaries:
        add_docs(table_summaries, tables, doc_type="table")
    if image_summaries:
        add_docs(image_summaries, clip_embeddings, doc_type="image", paths=image_paths)

    return retriever
