from rest_framework import serializers


class DocumentSerializer(serializers.Serializer):
    file_path = serializers.CharField(max_length=1024)
    name = serializers.CharField(max_length=512)
