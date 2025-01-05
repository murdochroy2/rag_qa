"""
This module contains API views for handling document ingestion and selection.
"""
import time
from django.db import transaction

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
import hashlib
import json
from django.http import HttpResponse
from rag_qa.core.models import Question
from django.views.decorators.csrf import csrf_exempt

from rag_qa.core.tasks import get_rag_response
from rag_qa.core.models import Document, Question
from rag_qa.core.api.serializers import DocumentSelectionSerializer, DocumentSerializer, QuestionSerializer
from rag_qa.core.tasks import build_index

from django.http import JsonResponse
from celery.result import AsyncResult

class DocumentIngestView(APIView):
    """
    Handles the ingestion of documents into the system.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Ingests a document into the system.
        
        :param request: The request containing the document details.
        :return: A response indicating the success or failure of the ingestion.
        """
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            file_path = serializer.validated_data["file_path"]
            name = serializer.validated_data["name"]
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        document = self._save_document(file_path, name)
        self._process_document(document)

        return Response(
            {"message": "Document ingested successfully", "file_path": file_path},
            status=status.HTTP_201_CREATED,
        )
    
    def _save_document(self, file_path, name):
        """
        Saves a document to the database.
        
        :param file_path: The path to the document file.
        :param name: The name of the document.
        :return: The saved document instance.
        """
        document = Document(file_path=file_path, name=name)
        document.save()
        return document

    def _process_document(self, document):
        """
        Initiates the processing of a document after it has been saved.
        
        :param document: The document instance to be processed.
        """
        document_id = document.id
        transaction.on_commit(func=lambda: build_index.apply_async(args=[document_id]))

    
class DocumentSelectionView(APIView):
    """
    Handles the selection of documents for processing.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Retrieves a list of all documents in the system.
        
        :param request: The request for the list of documents.
        :return: A response containing the list of documents.
        """
        documents = Document.objects.all() # TODO: Filter by indexed documents
        serializer = DocumentSelectionSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Updates the selection status of documents.
        
        :param request: The request containing the document selection details.
        :return: A response indicating the success or failure of the update.
        """
        serializer = DocumentSelectionSerializer(data=request.data, many=True)
        if serializer.is_valid():
            for details in serializer.validated_data:
                document = Document.objects.filter(id=details["id"]).update(selected=details["selected"])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionAnswerView(APIView):
    """
    Handles the processing of questions and retrieval of answers.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Processes a question and retrieves an answer.
        
        :param request: The request containing the question.
        :return: A response containing the answer and the status of the processing.
        """
        serializer = QuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.validated_data["question"]
        documents = self._get_documents()
        question_id = hashlib.md5(f"{documents}_{question}".encode()).hexdigest()
        model_object, created = Question.objects.get_or_create(question_id=question_id)

        if model_object.status == 'in_progress':
            answer = self._check_progress(model_object)
        else:
            answer = self._initiate_task(model_object, documents, question)

        return Response({"answer": answer, "status": model_object.status}, status=status.HTTP_200_OK)

    def _get_documents(self):
        """
        Retrieves a tuple of IDs of documents that are selected for processing.
        
        :return: A tuple of document IDs.
        """
        return tuple(Document.objects.filter(selected=True).order_by("id").values_list("id", flat=True))

    def _check_progress(self, model_object):
        """
        Checks the progress of a question processing task.
        
        :param model_object: The model object representing the question.
        :return: The answer to the question or a status message.
        """
        task = AsyncResult(model_object.answer_id)
        if task.ready():
            if task.status == 'SUCCESS':
                answer = task.get()
                model_object.status = 'success'
            else:
                answer = ""
                model_object.status = 'failed'
            model_object.save()
        else:
            answer = "thinking..."
        return answer

    def _initiate_task(self, model_object, documents, question):
        """
        Initiates the processing of a question.
        
        :param model_object: The model object representing the question.
        :param documents: A tuple of document IDs.
        :param question: The question to be processed.
        :return: A status message indicating the initiation of processing.
        """
        task = get_rag_response.apply_async(args=[documents, question])
        model_object.answer_id = task.id
        model_object.status = 'in_progress'
        model_object.save()
        return "thinking..."
