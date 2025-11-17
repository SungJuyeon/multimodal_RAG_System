import uuid
from langchain_core.documents import Document
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

def create_vectorstore(collection_name="sample-rag-multi-modal"):
    return Chroma(collection_name=collection_name, embedding_function=OpenAIEmbeddings())

def create_multi_vector_retriever(vectorstore, text_summaries, texts, table_summaries, tables, image_summaries, images):
    store = InMemoryStore()
    retriever = MultiVectorRetriever(vectorstore=vectorstore, docstore=store, id_key="doc_id")

    def add_docs(summaries, contents):
        ids = [str(uuid.uuid4()) for _ in contents]
        summary_docs = [Document(page_content=s, metadata={"doc_id": ids[i]}) for i, s in enumerate(summaries)]
        retriever.vectorstore.add_documents(summary_docs)
        retriever.docstore.mset(list(zip(ids, contents)))

    if text_summaries:
        add_docs(text_summaries, texts)
    if table_summaries:
        add_docs(table_summaries, tables)
    if image_summaries:
        add_docs(image_summaries, images)

    return retriever