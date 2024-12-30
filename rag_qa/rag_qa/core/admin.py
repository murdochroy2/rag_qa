from django.contrib import admin

# Register your models here.
from rag_qa.core.models import Document, Question

admin.site.register(Document)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ("file_path", "created_at")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_id", "status", "answer_id")
    