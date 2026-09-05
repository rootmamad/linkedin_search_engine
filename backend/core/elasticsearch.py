from elasticsearch import Elasticsearch
from backend.core.config import settings

es_host = settings.ELASTICSEARCH_HOST
if not es_host.startswith(("http://", "https://")):
    es_host = f"http://{es_host}:9200"

es_client = Elasticsearch(es_host)
INDEX_NAME = "linkedin_profiles"
#elasticsearch index name

def create_index_if_not_exists():
    """creating index for data"""
    if es_client.indices.exists(index=INDEX_NAME):
        return

    settings = {
        "analysis": {
            "filter": {
                "my_phonetic": {
                    "type": "phonetic",
                    "encoder": "metaphone",
                    "replace": False
                }
            },
            "analyzer": {
                "phonetic_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["lowercase", "my_phonetic"]
                },
                "standard_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["lowercase", "stop"]
                }
            }
        }
    }
    #mapping structure
    mapping = {
        "settings": settings,
        "mappings": {
            "properties": {
                "id": {"type": "long"},
                "full_name": {
                    "type": "text",
                    "analyzer": "standard_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256},
                        "phonetic": {"type": "text", "analyzer": "phonetic_analyzer"},
                        "ngram": {
                            "type": "text",
                            "analyzer": "autocomplete",
                            "search_analyzer": "standard"
                        }
                    }
                },
                "job_title": {
                    "type": "text",
                    "analyzer": "standard_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256},
                        "phonetic": {"type": "text", "analyzer": "phonetic_analyzer"}
                    }
                },
                "company_name": {
                    "type": "text",
                    "analyzer": "standard_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256},
                        "phonetic": {"type": "text", "analyzer": "phonetic_analyzer"}
                    }
                },
                "summary": {
                    "type": "text",
                    "analyzer": "standard_analyzer"
                },
                "skills": {"type": "keyword"},
                "job_title_role": {"type": "keyword"},
                "job_title_levels": {"type": "keyword"},
                "company_industry": {"type": "keyword"},
                "company_country": {"type": "keyword"},
                "location_country": {"type": "keyword"},
                "location_region": {"type": "keyword"},
                "phone_numbers": {"type": "keyword"},
                "emails": {
                    "type": "nested",
                    "properties": {
                        "address": {"type": "keyword"},
                        "type": {"type": "keyword"}
                    }
                },
                "facebook_url": {"type": "keyword"},
                "created_at": {"type": "date"}
            }
        }
    }

    mapping["settings"]["analysis"]["analyzer"]["autocomplete"] = {
        "tokenizer": "autocomplete",
        "filter": ["lowercase"]
    }
    mapping["settings"]["analysis"]["tokenizer"] = {
        "autocomplete": {
            "type": "edge_ngram",
            "min_gram": 2,
            "max_gram": 10,
            "token_chars": ["letter", "digit"]
        }
    }

    es_client.indices.create(index=INDEX_NAME, body=mapping)