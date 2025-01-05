import hashlib
from django.test import TestCase
from django.urls import reverse
from rag_qa.core.api.views import QuestionAnswerView
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from rag_qa.core.models import Document, Question
from rag_qa.core.api.serializers import DocumentSerializer, DocumentSelectionSerializer, QuestionSerializer

class DocumentIngestViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api:document-ingest')
        self.assertTrue(self.url)
        self.valid_payload = {
            'file_path': '/path/to/test/document.pdf',
            'name': 'Test Document'
        }

    @patch('rag_qa.core.tasks.build_index.apply_async')
    def test_create_document_success(self, mock_build_index):
        """Test successful document creation"""
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)

    def test_create_document_invalid_data(self):
        """Test document creation with invalid data"""
        invalid_payload = {'file_path': ''}
        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Document.objects.count(), 0)

class DocumentSelectionViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api:document-selection')
        self.doc1 = Document.objects.create(
            file_path='/path/to/doc1.pdf',
            name='Doc 1',
            selected=True
        )
        self.doc2 = Document.objects.create(
            file_path='/path/to/doc2.pdf',
            name='Doc 2',
            selected=False
        )

    def test_get_documents(self):
        """Test retrieving all documents"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_update_document_selection(self):
        """Test updating document selection status"""
        payload = [
            {'id': self.doc1.id, 'selected': False},
            {'id': self.doc2.id, 'selected': True}
        ]
        response = self.client.put(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doc1.refresh_from_db()
        self.doc2.refresh_from_db()
        self.assertFalse(self.doc1.selected)
        self.assertTrue(self.doc2.selected)

class QuestionAnswerViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api:question-answer')
        self.doc = Document.objects.create(
            file_path='/path/to/doc.pdf',
            name='Test Doc',
            selected=True
        )
        self.valid_payload = {
            'question': 'What is the meaning of life?'
        }

    @patch('rag_qa.core.tasks.get_rag_response.apply_async')
    def test_ask_new_question(self, mock_get_response):
        """Test asking a new question"""
        mock_task = MagicMock()
        mock_task.id = 'test-task-id'
        mock_get_response.return_value = mock_task

        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['answer'], 'thinking...')
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertTrue(mock_get_response.called)

    def test_ask_question_invalid_data(self):
        """Test asking question with invalid data"""
        invalid_payload = {'question': None}
        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('celery.result.AsyncResult')
    @patch.object(QuestionAnswerView, '_check_task_status')
    def test_check_existing_question_completed(self, mock_check_task_status, mock_async_result):
        """Test checking status of completed question"""
        # Create a question with existing task
        question = self.valid_payload.get('question')
        documents = tuple(Document.objects.filter(selected=True).order_by("id").values_list("id", flat=True))
        print(f"Documents in test: {documents}")
        question_id = hashlib.md5(f"{documents}_{question}".encode()).hexdigest()
        print(f"Question ID in test: {question_id}")
        question = Question.objects.create(
            question_id=question_id,
            answer_id='test-task-id',
            status='in_progress'
        )
        
        # Mock the task result
        mock_task = MagicMock()
        mock_task.ready.return_value = True
        mock_task.successful.return_value = True
        mock_task.status = 'SUCCESS'
        mock_task.get.return_value = '42'
        mock_async_result.return_value = mock_task

        mock_check_task_status.return_value = '42'

        # Ask the same question again
        response = self.client.post(self.url, self.valid_payload, format='json')

        # mock_async_result.assert_called()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['answer'], '42')