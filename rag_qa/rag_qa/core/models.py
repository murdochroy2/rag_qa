from django.db import models


# Create your models here.
class Document(models.Model):
    name = models.CharField(null=False, blank=False, max_length=512)
    file_path = models.CharField(null=False, blank=False, max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    indexed = models.BooleanField(default=False)
    selected = models.BooleanField(default=False)

class Question(models.Model):
    question_id = models.CharField(max_length=2048, null=False, blank=False)
    status = models.CharField(
        choices=[('in_progress', 'in_progress'), ('sucess', 'success'), ('failed', 'failed')], 
        max_length=20),
    answer_id = models.CharField(max_length=64)
