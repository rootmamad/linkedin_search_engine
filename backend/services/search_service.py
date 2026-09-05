from typing import List, Dict, Any, Optional
import logging
from fastapi import HTTPException
from elasticsearch import TransportError
from psycopg2.extras import RealDictCursor
from backend.core.database import get_db_connection
from backend.schemas.user import PersonFilterParams, PaginatedPersonResponse, PersonDetailResponse
from backend.core.elasticsearch import INDEX_NAME
from backend.core.config import settings
#heart of searching
logger = logging.getLogger(__name__)

#full-text search structure 
_TEXT_FIELDS = [
    "full_name^6",
    "full_name.phonetic^4",
    "job_title^4",
    "job_title.phonetic^3",
    "company_name^3",
    "company_name.phonetic^2",
    "summary^2",
    "experiences.job_title^2",
    "experiences.company_name^2",
    "educations.school_name^1",
    "educations.majors^1",
]

def build_es_query(params: PersonFilterParams) -> Dict[str, Any]:
    must_clauses = []
    should_clauses = []
    filter_clauses = []

    q = (params.q or "").strip()
    if q:
        must_clauses.append({
            "multi_match": {
                "query": q,
                "type": "best_fields",
                "fields": _TEXT_FIELDS,
                "operator": "and",
                "fuzziness": "AUTO",
                "prefix_length": 1,
                "max_expansions": 50,
                "boost": 4.0,
            }
        })

        should_clauses.append({
            "multi_match": {
                "query": q,
                "type": "best_fields",
                "fields": _TEXT_FIELDS,
                "operator": "or",
                "minimum_should_match": "1",
                "fuzziness": "AUTO",
                "prefix_length": 1,
                "max_expansions": 50,
                "boost": 1.0,
            }
        })

        should_clauses.append({
            "match": {
                "full_name.ngram": {
                    "query": q,
                    "boost": 2.0
                }
            }
        })

        should_clauses.append({
            "match": {
                "skills": {
                    "query": q,
                    "fuzziness": "AUTO",
                    "boost": 1.5
                }
            }
        })

    else:
        must_clauses.append({"match_all": {}})

    def add_term(field: str, value: Optional[str]) -> None:
        if value and value.strip():
            filter_clauses.append({"term": {field: value.strip().lower()}})
    #adding filters 
    add_term("job_title_role", params.job_title_role)
    add_term("company_industry", params.company_industry)
    add_term("company_country", params.company_country)
    add_term("location_country", params.location_country)
    add_term("location_region", params.location_region)
    #multy select filters
    if params.job_title_levels:
        levels = [lvl.strip().lower() for lvl in params.job_title_levels if lvl and lvl.strip()]
        if levels:
            filter_clauses.append({
                "bool": {
                    "should": [{"term": {"job_title_levels": level}} for level in levels],
                    "minimum_should_match": 1
                }
            })



    if params.skills:
        skills = [skill.strip().lower() for skill in params.skills if skill and skill.strip()]
        if skills:
            filter_clauses.append({
                "bool": {
                    "should": [{"term": {"skills": skill}} for skill in skills],
                    "minimum_should_match": 1
                }
            })
    #main query
    query = {
        "bool": {
            "must": must_clauses,
            "filter": filter_clauses,
        }
    }
    if should_clauses:
        query["bool"]["should"] = should_clauses

    return {
        "query": query,
        "size": params.page_size,
        "from": (params.page - 1) * params.page_size,
        "track_total_hits": True,
        "_source": ["id"], 
    }

def fetch_full_data_from_pg(person_ids: List[int]) -> List[dict]:
    if not person_ids:
        return []
    #query for getting data from postgresql
    query = """
        SELECT 
            p.*,
            COALESCE(
                (
                    SELECT json_agg(json_build_object(
                        'id', e.id,
                        'company_name', e.company_name,
                        'job_title', e.job_title
                    ))
                    FROM experiences e 
                    WHERE e.person_id = p.id
                ), '[]'::json
            ) AS experiences,
            COALESCE(
                (
                    SELECT json_agg(json_build_object(
                        'id', ed.id,
                        'school_name', ed.school_name,
                        'degrees', ed.degrees,
                        'majors', ed.majors
                    ))
                    FROM educations ed 
                    WHERE ed.person_id = p.id
                ), '[]'::json
            ) AS educations
        FROM people p
        WHERE p.id = ANY(%s);
    """
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (person_ids,))
            return cur.fetchall()

def search_and_get_profiles(es_client, params: PersonFilterParams) -> PaginatedPersonResponse:
    es_query = build_es_query(params)
    #main searching func
    try:
        response = es_client.search(
            index=INDEX_NAME,
            body=es_query,
            request_timeout=getattr(settings, "ES_TIMEOUT", 15)
        )
    except TransportError as e:
        logger.error(f"Elasticsearch error: {e}")
        raise HTTPException(status_code=503, detail="Search backend unavailable")
    except Exception as e:
        logger.error(f"Unexpected error during ES search: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    hits = response.get("hits", {}).get("hits", [])
    total = response.get("hits", {}).get("total", {}).get("value", 0)

    if not hits:
        return PaginatedPersonResponse(
            total=total,
            page=params.page,
            page_size=params.page_size,
            items=[]
        )

    es_ids = []
    scores = {}
    for hit in hits:
        if "_source" in hit and "id" in hit["_source"]:
            pid = hit["_source"]["id"]
            es_ids.append(pid)
            scores[pid] = hit.get("_score")

    pg_data = fetch_full_data_from_pg(es_ids)
    #order profiles based on results
    pg_dict = {row["id"]: row for row in pg_data}
    ordered_profiles = []
    for pid in es_ids:
        if pid in pg_dict:
            row = pg_dict[pid]
            row["score"] = scores.get(pid)
            ordered_profiles.append(row)
        else:
            logger.warning(f"ES id {pid} not found in PostgreSQL – skipping")

    items = [PersonDetailResponse(**profile) for profile in ordered_profiles]
    #normalaztion data with schemas
    return PaginatedPersonResponse(
        total=total,
        page=params.page,
        page_size=params.page_size,
        items=items
    )