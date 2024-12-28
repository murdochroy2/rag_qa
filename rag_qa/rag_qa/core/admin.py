from django.contrib import admin

# Register your models here.
from rag_qa.core.models import Document

admin.site.register(Document)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ("file_path", "created_at")
