# Create your views here.
import time
from django.db import transaction

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rag_qa.core.models import Document
from rag_qa.core.api.serializers import DocumentSelectionSerializer, DocumentSerializer
from rag_qa.core.tasks import build_index

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
