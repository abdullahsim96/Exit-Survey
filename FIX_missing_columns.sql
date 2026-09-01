-- ============================================================
-- FIX: Run this entire script once in the Supabase SQL Editor.
-- It safely adds every column the app currently expects, using
-- IF NOT EXISTS so it will not error even if some columns
-- already exist. This resolves the "Could not find the 'crm'
-- column" error (and prevents the same error for any other
-- column the live table might be missing).
-- ============================================================

alter table exit_survey_responses add column if not exists small_team text;
alter table exit_survey_responses add column if not exists crm text;
alter table exit_survey_responses add column if not exists survey_language text;
alter table exit_survey_responses add column if not exists link_token text;

alter table exit_survey_responses add column if not exists role_onboard_training int;
alter table exit_survey_responses add column if not exists role_ongoing_training int;

alter table exit_survey_responses add column if not exists vendor_support int;
alter table exit_survey_responses add column if not exists vendor_hr_services int;
alter table exit_survey_responses add column if not exists vendor_text text;

alter table exit_survey_responses add column if not exists would_recommend text;

-- If your table also predates these, this makes sure they exist too:
alter table exit_survey_responses add column if not exists workload_deadlines_realistic int;
alter table exit_survey_responses add column if not exists comp_benefits_satisfaction int;
alter table exit_survey_responses add column if not exists culture_overall text;
alter table exit_survey_responses add column if not exists culture_text text;
alter table exit_survey_responses add column if not exists primary_reason text;
alter table exit_survey_responses add column if not exists primary_reason_other text;
alter table exit_survey_responses add column if not exists would_return text;
alter table exit_survey_responses add column if not exists other_comments text;

-- Make sure the survey_links table exists (needed for the Admin: Links tab)
create table if not exists survey_links (
    id bigint generated always as identity primary key,
    created_at timestamptz default now(),
    token text unique not null,
    label text,
    deadline timestamptz,
    is_active boolean default true
);
alter table survey_links enable row level security;
