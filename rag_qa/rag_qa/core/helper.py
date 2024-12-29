import os
from django.conf import settings
from django.core.management.base import BaseCommand
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
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