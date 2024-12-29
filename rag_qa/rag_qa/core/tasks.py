import time
from celery import shared_task
from rag_qa.core.helper import update_vector_db

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