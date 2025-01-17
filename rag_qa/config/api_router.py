from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from rag_qa.core.api.views import DocumentIngestView, DocumentSelectionView, QuestionAnswerView
from rag_qa.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls + [
    path("document/", DocumentIngestView.as_view(), name="document-ingest"),
    path("document/selection/", DocumentSelectionView.as_view(), name="document-selection"),
    path("question-answer/", QuestionAnswerView.as_view(), name="question-answer"),
]
