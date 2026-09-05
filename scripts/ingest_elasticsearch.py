import json
import logging
import os
from typing import Any, Dict, List, Optional

from elasticsearch import helpers

from backend.core.config import settings
from backend.core.elasticsearch import es_client, INDEX_NAME, create_index_if_not_exists

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ingest_es")


def load_records(path: str) -> List[Dict[str, Any]]:
    """loading data from json"""
    records = []
    if os.path.isdir(path):
        files = [f for f in os.listdir(path) if f.endswith(".json")]
        for fname in files:
            with open(os.path.join(path, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    records.extend(data)
                elif isinstance(data, dict):
                    records.append(data)
    else:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                records = [data]
    logger.info(f"Loaded {len(records)} records from {path}")
    return records


def normalize(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """normalization and cleaning data"""
    person_id = record.get("id")
    if person_id is None:
        logger.warning(f"Skipping record without 'id': {record.get('full_name')}")
        return None
    try:
        person_id = int(person_id)
    except (TypeError, ValueError):
        logger.warning(f"Invalid id: {record.get('id')}")
        return None

    def to_str_lower(v):
        return None if v is None else str(v).lower()

    def to_list_lower(v):
        if v is None:
            return []
        if isinstance(v, list):
            return [str(item).lower() for item in v if item is not None]
        return [str(v).lower()]

    return {
        "id": person_id,
        "full_name": to_str_lower(record.get("full_name")),
        "gender": to_str_lower(record.get("gender")),
        "linkedin_url": to_str_lower(record.get("linkedin_url")),
        "job_title": to_str_lower(record.get("job_title")),
        "job_title_role": to_str_lower(record.get("job_title_role")),
        "job_title_levels": to_list_lower(record.get("job_title_levels")),
        "company_name": to_str_lower(record.get("company_name")),
        "company_industry": to_str_lower(record.get("company_industry")),
        "company_country": to_str_lower(record.get("company_country")),
        "company_region": to_str_lower(record.get("company_region")),
        "location_country": to_str_lower(record.get("location_country")),
        "location_region": to_str_lower(record.get("location_region")),
        "summary": to_str_lower(record.get("summary")),
        "skills": to_list_lower(record.get("skills")),
        "phone_numbers": [str(p) for p in record.get("phone_numbers") or []],
        "emails": record.get("emails") or [],
        "facebook_url": to_str_lower(record.get("facebook_url")),
        "created_at": record.get("created_at") or "2026-01-01T00:00:00Z"
    }


def index_bulk(records: List[Dict[str, Any]]) -> int:
    actions = []
    for rec in records:
        doc = normalize(rec)
        if doc is None:
            continue
        actions.append({
            "_index": INDEX_NAME,
            "_id": doc["id"],
            "_source": doc
        })

    if not actions:
        return 0

    success, failed = helpers.bulk(
        es_client, actions,
        stats_only=True,
        raise_on_error=False,
        request_timeout=60
    )
    if failed:
        logger.error(f"Bulk indexing failed for {failed} documents")
    logger.info(f"Successfully indexed {success} documents")
    return success


def main():
    """Sends all actions in a single bulk request"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="data/data.json")
    args = parser.parse_args()

    create_index_if_not_exists()
    records = load_records(args.path)
    if not records:
        logger.error("No records found")
        return

    indexed = index_bulk(records)
    logger.info(f"Done. Total indexed: {indexed}")


if __name__ == "__main__":
    main()