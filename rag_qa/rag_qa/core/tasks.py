import time
from celery import shared_task
from rag_qa.core.helper import query_vector_db, update_vector_db

from .models import Document

@shared_task()
def build_index(document_id):
    try:
        update_vector_db(document_id)
    except:
        return
    document = Document.objects.get(id=document_id)
    document.indexed = True
    document.save()

@shared_task()
def get_rag_response(self, documents: tuple[int], query: str):
    document_names = _get_document_names(documents)
    result = query_vector_db(documents, query)
    return result

def _get_document_names(documents):
    return list(Document.objects.filter(id__in=documents).values_list("name", flat=True))