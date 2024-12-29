# Create your views here.
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
    permission_classes = [AllowAny]

    def post(self, request):
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
        document = Document(file_path=file_path, name=name)
        document.save()
        return document

    def _process_document(self, document):
        document_id = document.id
        transaction.on_commit(func=lambda: build_index.apply_async(args=[document_id]))

    
class DocumentSelectionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        documents = Document.objects.all()
        serializer = DocumentSelectionSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = DocumentSelectionSerializer(data=request.data, many=True)
        if serializer.is_valid():
            for details in serializer.validated_data:
                document = Document.objects.filter(id=details["id"]).update(selected=details["selected"])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionAnswerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.validated_data["question"]
        documents = self._get_documents()
        question_id = hashlib.md5(f"{documents}_{question}".encode()).hexdigest()
        model_object, created = Question.objects.get_or_create(question_id=question_id)

        if model_object.status == 'in_progress':
            answer = self._check_task_status(model_object)
        else:
            answer = self._initiate_task(model_object, documents, question)

        return Response({"answer": answer, "status": model_object.status}, status=status.HTTP_200_OK)

    def _get_documents(self):
        return tuple(Document.objects.filter(selected=True).order_by("id").values_list("id", flat=True))

    def _check_task_status(self, model_object):
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
        task = get_rag_response.apply_async(args=[documents, question])
        model_object.answer_id = task.id
        model_object.status = 'in_progress'
        model_object.save()
        return "thinking..."
