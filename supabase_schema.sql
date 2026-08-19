create table exit_survey_responses (
    id bigint generated always as identity primary key,
    created_at timestamptz default now(),

    department text,
    job_title text,
    tenure text,
    employment_type text,
    departure_type text,

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
    burnout_frequency text,

    comp_fair int,
    comp_market_competitive int,
    comp_benefits_satisfaction int,
    comp_was_factor text,

    culture_respect int,
    culture_belonging int,
    culture_values_alignment int,
    culture_overall text,
    culture_text text,

    location_fit int,
    location_was_factor text,
    location_text text,

    primary_reason text,
    primary_reason_other text,
    enps_recommend_0_10 int,
    would_return text,
    retain_text text,
    other_comments text
);

-- Lock the table down: no public access at all.
-- The app connects with the service_role key, which bypasses RLS,
-- so this keeps the data safe even if someone finds your Supabase URL.
alter table exit_survey_responses enable row level security;
