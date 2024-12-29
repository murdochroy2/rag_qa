from django.db import models


# Create your models here.
class Document(models.Model):
    name = models.CharField(null=False, blank=False, max_length=512)
    file_path = models.CharField(null=False, blank=False, max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    indexed = models.BooleanField(default=False)
    selected = models.BooleanField(default=False)
