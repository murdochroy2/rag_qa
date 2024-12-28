# Create your views here.

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rag_qa.core.models import Document
from rag_qa.core.serializers import DocumentSerializer


class DocumentIngestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            file_path = serializer.validated_data["file_path"]
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Assuming there's a model named Document with a field named file_url
        Document.objects.create(file_path=file_path)

        return Response(
            {"message": "Document ingested successfully", "file_path": file_path},
            status=status.HTTP_201_CREATED,
        )
