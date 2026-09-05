import argparse
import json
import logging
import os
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import execute_values, Json

from backend.core.config import settings
#ingesting data to postgresql 
DB_CONFIG = {
    "dbname": settings.POSTGRES_DB,
    "user": settings.POSTGRES_USER,
    "password": settings.POSTGRES_PASSWORD,
    "host": settings.POSTGRES_HOST,
    "port": settings.POSTGRES_PORT,
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("people_importer")

PEOPLE_UPSERT_SQL = """
INSERT INTO people (
    id, full_name, gender, linkedin_url, job_title, job_title_role, job_title_levels,
    company_name, company_industry, company_country, company_region,
    location_country, location_region, summary, skills, phone_numbers, emails, facebook_url
) VALUES (
    %(id)s, %(full_name)s, %(gender)s, %(linkedin_url)s, %(job_title)s, %(job_title_role)s, %(job_title_levels)s,
    %(company_name)s, %(company_industry)s, %(company_country)s, %(company_region)s,
    %(location_country)s, %(location_region)s, %(summary)s, %(skills)s, %(phone_numbers)s, %(emails)s, %(facebook_url)s
)
ON CONFLICT (id) DO UPDATE SET
    full_name = EXCLUDED.full_name,
    gender = EXCLUDED.gender,
    linkedin_url = EXCLUDED.linkedin_url,
    job_title = EXCLUDED.job_title,
    job_title_role = EXCLUDED.job_title_role,
    job_title_levels = EXCLUDED.job_title_levels,
    company_name = EXCLUDED.company_name,
    company_industry = EXCLUDED.company_industry,
    company_country = EXCLUDED.company_country,
    company_region = EXCLUDED.company_region,
    location_country = EXCLUDED.location_country,
    location_region = EXCLUDED.location_region,
    summary = EXCLUDED.summary,
    skills = EXCLUDED.skills,
    phone_numbers = EXCLUDED.phone_numbers,
    emails = EXCLUDED.emails,
    facebook_url = EXCLUDED.facebook_url;
"""

DELETE_EXPERIENCES_SQL = "DELETE FROM experiences WHERE person_id = %s;"
DELETE_EDUCATIONS_SQL = "DELETE FROM educations WHERE person_id = %s;"

INSERT_EXPERIENCES_SQL = "INSERT INTO experiences (person_id, company_name, job_title) VALUES %s"
INSERT_EXPERIENCES_TEMPLATE = "(%(person_id)s, %(company_name)s, %(job_title)s)"

INSERT_EDUCATIONS_SQL = "INSERT INTO educations (person_id, school_name, degrees, majors) VALUES %s"
INSERT_EDUCATIONS_TEMPLATE = "(%(person_id)s, %(school_name)s, %(degrees)s, %(majors)s)"


def load_records(json_path: str) -> List[Dict[str, Any]]:
    """load records from json file"""

    records: List[Dict[str, Any]] = []

    if os.path.isdir(json_path):
        files = sorted(f for f in os.listdir(json_path) if f.lower().endswith(".json"))
        if not files:
            logger.error(f"No JSON files found in directory: {json_path}")
            return records
        for filename in files:
            file_path = os.path.join(json_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                logger.error(f"Failed to read/parse file '{file_path}': {exc}")
                continue
            if isinstance(data, list):
                records.extend(data)
            elif isinstance(data, dict):
                records.append(data)
            else:
                logger.error(f"Unsupported JSON structure in file '{file_path}'")
        logger.info(f"Loaded {len(records)} record(s) from {len(files)} file(s) in directory '{json_path}'")
    else:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error(f"Failed to read/parse file '{json_path}': {exc}")
            return records
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = [data]
        else:
            logger.error(f"Unsupported JSON structure in file '{json_path}'")
        logger.info(f"Loaded {len(records)} record(s) from file '{json_path}'")

    return records


def to_str_or_none(value: Any) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def to_list_or_none(value: Any, context: str = "") -> Optional[List[Any]]:
    if value is None:
        return None
    if isinstance(value, list):
        return value
    logger.warning(f"{context}: expected a list but got {type(value).__name__}, coercing to single-item list: {value!r}")
    return [value]


def normalize_person(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """normalize and cleaning json data"""
    raw_id = record.get("id")
    if raw_id is None:
        logger.error(f"Skipping record with missing 'id' field: full_name={record.get('full_name')!r}")
        return None
    try:
        person_id = int(raw_id)
    except (TypeError, ValueError):
        logger.error(f"Skipping record with invalid 'id' value: {raw_id!r}")
        return None

    emails = record.get("emails")

    return {
        "id": person_id,
        "full_name": to_str_or_none(record.get("full_name")),
        "gender": to_str_or_none(record.get("gender")),
        "linkedin_url": to_str_or_none(record.get("linkedin_url")),
        "job_title": to_str_or_none(record.get("job_title")),
        "job_title_role": to_str_or_none(record.get("job_title_role")),
        "job_title_levels": to_list_or_none(record.get("job_title_levels"), f"person id={person_id}"),
        "company_name": to_str_or_none(record.get("company_name")),
        "company_industry": to_str_or_none(record.get("company_industry")),
        "company_country": to_str_or_none(record.get("company_country")),
        "company_region": to_str_or_none(record.get("company_region")),
        "location_country": to_str_or_none(record.get("location_country")),
        "location_region": to_str_or_none(record.get("location_region")),
        "summary": to_str_or_none(record.get("summary")),
        "skills": to_list_or_none(record.get("skills"), f"person id={person_id}"),
        "phone_numbers": to_list_or_none(record.get("phone_numbers"), f"person id={person_id}"),
        "emails": Json(emails) if emails is not None else None,
        "facebook_url": to_str_or_none(record.get("facebook_url")),
    }


def normalize_experiences(person_id: int, items: Any) -> List[Dict[str, Any]]:
    """normalize and cleaning json data"""

    if items is None:
        return []
    if not isinstance(items, list):
        logger.warning(f"person id={person_id}: 'experience' is not a list, ignoring value: {items!r}")
        return []

    normalized = []
    for item in items:
        if not isinstance(item, dict):
            logger.warning(f"person id={person_id}: skipping invalid experience entry: {item!r}")
            continue
        normalized.append({
            "person_id": person_id,
            "company_name": to_str_or_none(item.get("company_name")),
            "job_title": to_str_or_none(item.get("job_title")),
        })
    return normalized


def normalize_educations(person_id: int, items: Any) -> List[Dict[str, Any]]:
    """normalize and cleaning json data"""

    if items is None:
        return []
    if not isinstance(items, list):
        logger.warning(f"person id={person_id}: 'education' is not a list, ignoring value: {items!r}")
        return []

    normalized = []
    for item in items:
        if not isinstance(item, dict):
            logger.warning(f"person id={person_id}: skipping invalid education entry: {item!r}")
            continue
        normalized.append({
            "person_id": person_id,
            "school_name": to_str_or_none(item.get("school_name")),
            "degrees": to_list_or_none(item.get("degrees"), f"person id={person_id}") or [],
            "majors": to_list_or_none(item.get("majors"), f"person id={person_id}") or [],
        })
    return normalized


def import_person(cursor, person: Dict[str, Any], experiences: List[Dict[str, Any]], educations: List[Dict[str, Any]]) -> None:
    """run and execute queries"""
    cursor.execute(PEOPLE_UPSERT_SQL, person)


    cursor.execute(DELETE_EXPERIENCES_SQL, (person["id"],))
    cursor.execute(DELETE_EDUCATIONS_SQL, (person["id"],))

    if experiences:
        execute_values(cursor, INSERT_EXPERIENCES_SQL, experiences, template=INSERT_EXPERIENCES_TEMPLATE)

    if educations:
        execute_values(cursor, INSERT_EDUCATIONS_SQL, educations, template=INSERT_EDUCATIONS_TEMPLATE)


def run_import(json_path: str) -> None:
    records = load_records(json_path)
    if not records:
        logger.error("No records to import. Exiting.")
        return

    logger.info(f"Starting import of {len(records)} record(s)")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as exc:
        logger.error(f"Failed to connect to database: {exc}")
        return

    success_count = 0
    failed_ids: List[Any] = []

    try:
        for index, record in enumerate(records, start=1):
            person = normalize_person(record)
            if person is None:
                failed_ids.append(record.get("id", f"unknown[index={index}]"))
                continue

            experiences = normalize_experiences(person["id"], record.get("experience"))
            educations = normalize_educations(person["id"], record.get("education"))

            try:
                with conn.cursor() as cursor:
                    import_person(cursor, person, experiences, educations)
                conn.commit()
                success_count += 1
                logger.info(
                    f"Imported person id={person['id']} "
                    f"(full_name={person['full_name']!r}, experiences={len(experiences)}, educations={len(educations)})"
                )
            except psycopg2.Error as exc:
                conn.rollback()
                failed_ids.append(person["id"])
                logger.error(f"Failed to import person id={person['id']}: {exc}")
    finally:
        conn.close()

    logger.info(f"Import finished. Success: {success_count}, Failed: {len(failed_ids)}, Total: {len(records)}")
    if failed_ids:
        logger.warning(f"Failed record IDs: {failed_ids}")


def main() -> None:
    run_import("data/data.json")


if __name__ == "__main__":
    main()