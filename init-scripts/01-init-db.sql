CREATE EXTENSION IF NOT EXISTS pg_trgm;



CREATE TABLE people (
    id BIGINT PRIMARY KEY,

    full_name TEXT,
    gender TEXT,
    linkedin_url TEXT,

    job_title TEXT,
    job_title_role TEXT,
    job_title_levels TEXT[],

    company_name TEXT,
    company_industry TEXT,
    company_country TEXT,
    company_region TEXT,

    location_country TEXT,
    location_region TEXT,

    summary TEXT,

    skills TEXT[],
    phone_numbers TEXT[],
    emails JSONB,

    facebook_url TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);



CREATE TABLE experiences (
    id BIGSERIAL PRIMARY KEY,
    person_id BIGINT NOT NULL REFERENCES people(id) ON DELETE CASCADE,

    company_name TEXT,
    job_title TEXT
);

CREATE TABLE educations (
    id BIGSERIAL PRIMARY KEY,
    person_id BIGINT NOT NULL REFERENCES people(id) ON DELETE CASCADE,

    school_name TEXT,
    degrees TEXT[],
    majors TEXT[]
);






CREATE INDEX idx_people_job_title
    ON people (job_title);

CREATE INDEX idx_people_job_title_role
    ON people (job_title_role);

CREATE INDEX idx_people_company_name
    ON people (company_name);

CREATE INDEX idx_people_company_industry
    ON people (company_industry);

CREATE INDEX idx_people_location_country
    ON people (location_country);

CREATE INDEX idx_people_location_region
    ON people (location_region);




CREATE INDEX idx_people_skills_gin
    ON people USING GIN (skills);

CREATE INDEX idx_people_job_title_levels_gin
    ON people USING GIN (job_title_levels);




CREATE INDEX idx_experiences_person_id
    ON experiences (person_id);

CREATE INDEX idx_educations_person_id
    ON educations (person_id);



CREATE INDEX idx_people_full_name_trgm
    ON people USING GIN (full_name gin_trgm_ops);

CREATE INDEX idx_people_job_title_trgm
    ON people USING GIN (job_title gin_trgm_ops);

CREATE INDEX idx_people_company_name_trgm
    ON people USING GIN (company_name gin_trgm_ops);

CREATE INDEX idx_experiences_company_name_trgm
    ON experiences USING GIN (company_name gin_trgm_ops);

CREATE INDEX idx_experiences_job_title_trgm
    ON experiences USING GIN (job_title gin_trgm_ops);