from typing import List, Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
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


class ExperienceBase(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None


class EducationBase(BaseModel):
    school_name: Optional[str] = None
    degrees: List[str] = Field(default_factory=list)
    majors: List[str] = Field(default_factory=list)