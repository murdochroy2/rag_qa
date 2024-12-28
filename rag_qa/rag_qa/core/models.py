from django.db import models


# Create your models here.
class Document(models.Model):
    file_path = models.CharField(null=False, blank=False, max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
