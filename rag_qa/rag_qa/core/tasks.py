import time
from celery import shared_task
from rag_qa.core.helper import query_vector_db, update_vector_db

from .models import Document

@shared_task()
def build_index(document_id):
    """
    Builds an index for a given document ID. This task updates the vector database with the document's embeddings and marks the document as indexed in the database.

    Args:
        document_id (int): The ID of the document for which to build the index.

    Raises:
        Exception: If the index building process fails.
    """
    try:
        update_vector_db(document_id)
    except Exception as e:
        print(f"Failed to build index for document with ID {document_id}: {e}")
        raise
    document = Document.objects.get(id=document_id)
    document.indexed = True
    document.save()

@shared_task()
def get_rag_response(documents: tuple[int], query: str):
    """
    Retrieves a response from the vector database for a given query across a set of documents.

    Args:
        documents (tuple[int]): A tuple of document IDs for which to retrieve the response.
        query (str): The query string to search for in the vector database.

    Returns:
        str: The result of the query.
    """
    document_names = _get_document_names(documents)
    result = query_vector_db(document_names, query)
    return result

def _get_document_names(documents):
    """
    Retrieves the names of documents based on their IDs.

    Args:
        documents (tuple[int]): A tuple of document IDs.

    Returns:
        list[str]: A list of document names corresponding to the provided IDs.
    """
    return list(Document.objects.filter(id__in=documents).values_list("name", flat=True))