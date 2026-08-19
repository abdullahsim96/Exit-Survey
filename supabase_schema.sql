-- ============================================================
-- FRESH INSTALL: run this whole file if you have not created
-- the tables yet.
-- ============================================================

create table exit_survey_responses (
    id bigint generated always as identity primary key,
    created_at timestamptz default now(),

    department text,
    crm text,
    job_title text,
    survey_language text,
    link_token text,

    role_clarity int,
    role_tools int,
    role_match int,
    role_text text,

    mgr_communication int,
    mgr_feedback int,
    mgr_growth_support int,
    mgr_comfort_raising_concerns int,
    mgr_text text,

    workload_manageable int,
    workload_life_balance int,
    workload_deadlines_realistic int,

    comp_fair int,
    comp_market_competitive int,
    comp_benefits_satisfaction int,

    culture_respect int,
    culture_belonging int,
    culture_values_alignment int,
    culture_overall text,
    culture_text text,

    location_was_factor text,
    location_text text,

    primary_reason text,
    primary_reason_other text,
    enps_recommend_0_10 int,
    would_return text,
    other_comments text
);

create table survey_links (
    id bigint generated always as identity primary key,
    created_at timestamptz default now(),
    token text unique not null,
    label text,
    deadline timestamptz,
    is_active boolean default true
);

-- Lock both tables down: no public access at all.
-- The app connects with the service_role key, which bypasses RLS,
-- so this keeps the data safe even if someone finds your Supabase URL.
alter table exit_survey_responses enable row level security;
alter table survey_links enable row level security;


-- ============================================================
-- MIGRATING AN EXISTING TABLE: if exit_survey_responses already
-- exists with data in it, don't drop it — run only the lines
-- below that you haven't already applied.
-- ============================================================

-- Fields added over time:
-- alter table exit_survey_responses add column crm text;
-- alter table exit_survey_responses add column survey_language text;
-- alter table exit_survey_responses add column link_token text;

-- Fields removed from the form (safe to leave the columns in
-- place — they'll just stop receiving new data — or drop them
-- if you want to clean up):
-- alter table exit_survey_responses drop column if exists tenure;
-- alter table exit_survey_responses drop column if exists employment_type;
-- alter table exit_survey_responses drop column if exists departure_type;
-- alter table exit_survey_responses drop column if exists burnout_frequency;
-- alter table exit_survey_responses drop column if exists comp_was_factor;
-- alter table exit_survey_responses drop column if exists location_fit;
-- alter table exit_survey_responses drop column if exists retain_text;

-- New table for the admin link/deadline feature:
-- create table survey_links (
--     id bigint generated always as identity primary key,
--     created_at timestamptz default now(),
--     token text unique not null,
--     label text,
--     deadline timestamptz,
--     is_active boolean default true
-- );
-- alter table survey_links enable row level security;
