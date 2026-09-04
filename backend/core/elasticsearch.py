from elasticsearch import Elasticsearch
from backend.core.config import settings
es_host = settings.ELASTICSEARCH_HOST
if not es_host.startswith("http://") and not es_host.startswith("https://"):
    es_host = f"http://{es_host}:9200"
es_client = Elasticsearch(es_host)

INDEX_NAME = "linkedin_profiles"

def get_es_client() -> Elasticsearch:
    return es_client