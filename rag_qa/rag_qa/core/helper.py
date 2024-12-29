import os
from django.conf import settings
from django.core.management.base import BaseCommand

from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain.retrievers import MergerRetriever

from rag_qa.core.models import Document

def update_vector_db(document_id):
    document = Document.objects.get(id=document_id)

    loader = PyPDFLoader(document.file_path)
    pages = loader.load_and_split()

    embeddings = OpenAIEmbeddings()

    collection_name = document.name

    DATABASE_URL = _get_database_url()

    _create_database_object(pages, embeddings, collection_name, DATABASE_URL)

def _get_database_url():
    # Pgvector uses a different database
    DATABASE_URL = \
        os.getenv("DATABASE_URL") \
        .replace("postgres://", "postgresql://") \
        .replace("@postgres", "@pgvector")
        
    return DATABASE_URL

def _create_database_object(pages, embeddings, collection_name, DATABASE_URL):
    db = PGVector.from_documents(
        embedding=embeddings,
        documents=pages,
        collection_name=collection_name,
        connection_string=DATABASE_URL,
    )

def query_vector_db(collection_names, query):
    retriever = _get_retriever_object(collection_names)
    # create retrieval qa chain for answering questions
    qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=1), chain_type="stuff", retriever=retriever)

    result = qa.invoke(query).get("result")
    return result

def _get_retriever_object(collection_names):
    retrievers = []
    for collection_name in collection_names:
        # get the langchain db object from the database using the collection name
        db = _get_db_by_name(collection_name)
        # create a retriever object by calling the vectorstore.as_retriever() method
        retriever = db.as_retriever()
        retrievers.append(retriever)
    retriever = MergerRetriever(retrievers=retrievers)
    return retriever

def _get_db_by_name(collection_name):
    db = PGVector(
        collection_name=collection_name,
        connection_string=_get_database_url(),
        embedding_function=OpenAIEmbeddings(),
    )        

    return db