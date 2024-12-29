import os
from django.conf import settings
from django.core.management.base import BaseCommand
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from rag_qa.core.models import Document
from rag_qa.core.helper import update_vector_db



class Command(BaseCommand):
    help = "Builds a pgvector index"

    def add_arguments(self, parser):
        parser.add_argument('document_id', type=int, help='The ID of the document to be indexed')

    def handle(self, *args, **kwargs):
        document_id = kwargs['document_id']
        self.stdout.write(f"The provided document ID is: {document_id}")

        update_vector_db(document_id)
