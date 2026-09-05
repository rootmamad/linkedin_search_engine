from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
#schemas for responce and requests
class PersonFilterParams(BaseModel):
    q: Optional[str] = Field(None, description="سرچ متنی روی نام، عنوان شغلی، شرکت و خلاصه")
    
    job_title_role: Optional[str] = None
    job_title_levels: Optional[List[str]] = Field(default=None)

    company_industry: Optional[str] = None
    company_country: Optional[str] = None

    location_country: Optional[str] = None
    location_region: Optional[str] = None

    skills: Optional[List[str]] = Field(default=None)

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ExperienceResponse(BaseModel):
    id: int
    company_name: Optional[str] = None
    job_title: Optional[str] = None

class EducationResponse(BaseModel):
    id: int
    school_name: Optional[str] = None
    degrees: List[str] = Field(default_factory=list)
    majors: List[str] = Field(default_factory=list)

class PersonDetailResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    gender: Optional[str] = None
    linkedin_url: Optional[str] = None

    job_title: Optional[str] = None
    job_title_role: Optional[str] = None
    job_title_levels: List[str] = Field(default_factory=list)

    company_name: Optional[str] = None
    company_industry: Optional[str] = None
    company_country: Optional[str] = None
    company_region: Optional[str] = None

    location_country: Optional[str] = None
    location_region: Optional[str] = None

    summary: Optional[str] = None

    skills: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    emails: List[dict] = Field(default_factory=list)

    facebook_url: Optional[str] = None
    created_at: datetime

    experiences: List[ExperienceResponse] = Field(default_factory=list)
    educations: List[EducationResponse] = Field(default_factory=list)

class PaginatedPersonResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PersonDetailResponse]