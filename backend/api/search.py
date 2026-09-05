from fastapi import APIRouter
from backend.core.elasticsearch import es_client  
from backend.schemas.user import PersonFilterParams, PaginatedPersonResponse
from backend.services.search_service import search_and_get_profiles

router = APIRouter(prefix="/api/search", tags=["Search"])
#search endpoint 
@router.post("/", response_model=PaginatedPersonResponse)
def search_people(params: PersonFilterParams):
    return search_and_get_profiles(es_client, params)