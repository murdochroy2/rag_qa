from django.conf import settings
from django.core.management.base import BaseCommand
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from rag_qa.core.models import Document



class Command(BaseCommand):
    help = "Builds a pgvector index"

    def add_arguments(self, parser):
        parser.add_argument('document_id', type=int, help='The ID of the document to be indexed')

    def handle(self, *args, **kwargs):
        document_id = kwargs['document_id']
        self.stdout.write(f"The provided document ID is: {document_id}")

        document = Document.objects.get(id=document_id)
        print(document.file_path)

        loader = PyPDFLoader(document.file_path)
        pages = loader.load_and_split()

        embeddings = OpenAIEmbeddings()
        # texts = [doc.page_content for doc in documents]

        collection_name = document.document.name

        print(settings.DATABASE_URL)

        db = PGVector.from_documents(
            embedding=embeddings,
            documents=pages,
            collection_name=collection_name,
            connection_string=settings.DATABASE_URL,
        )