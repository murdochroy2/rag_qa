from django.conf import settings
from django.core.management.base import BaseCommand

from rag_qa.core.helper import query_vector_db

class Command(BaseCommand):
    help = "Queries a pgvector index by collection id"

    def add_arguments(self, parser):
        parser.add_argument('collection_names', type=str, nargs='+', help='The collection names to be queried')
        parser.add_argument('query', type=str, help='The query to be executed')

    def handle(self, collection_names, query, *args, **kwargs):
        result = query_vector_db(collection_names, query)
        print(result)