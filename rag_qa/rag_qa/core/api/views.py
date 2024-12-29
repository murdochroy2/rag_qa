# Create your views here.

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rag_qa.core.models import Document
from rag_qa.core.api.serializers import DocumentSerializer


class DocumentIngestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            file_path = serializer.validated_data["file_path"]
            name = serializer.validated_data["name"]
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        Document.objects.create(file_path=file_path, name=name)

        return Response(
            {"message": "Document ingested successfully", "file_path": file_path},
            status=status.HTTP_201_CREATED,
        )
