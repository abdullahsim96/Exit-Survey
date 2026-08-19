import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Employee Exit Survey", page_icon="📋", layout="centered")

TABLE_NAME = "exit_survey_responses"


@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

RATING_LABELS = {
    1: "1 - Strongly Disagree",
    2: "2 - Disagree",
    3: "3 - Neutral",
    4: "4 - Agree",
    5: "5 - Strongly Agree",
}

def rating_question(label, key):
    return st.radio(
        label,
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: RATING_LABELS[x],
        horizontal=True,
        key=key,
        index=None,
    )

# ----------------------------
# Header
# ----------------------------
st.title("📋 Employee Exit Survey")
st.markdown(
    "Thank you for taking the time to complete this survey. Your honest feedback "
    "helps us understand where we can improve. Responses are kept confidential and "
    "reviewed in aggregate. This should take about **7-10 minutes**."
)
st.divider()

# ----------------------------
# Form
# ----------------------------
with st.form("exit_survey_form", clear_on_submit=False):

    st.subheader("Section 1: Background")
    department = st.text_input("Department *")
    job_title = st.text_input("Job title *")
    tenure = st.selectbox(
        "Length of employment *",
        ["", "<6 months", "6-12 months", "1-2 years", "2-5 years", "5+ years"],
    )
    employment_type = st.selectbox(
        "Employment type *", ["", "Full-time", "Part-time", "Contract"]
    )
    departure_type = st.selectbox(
        "Is this departure *",
        ["", "Voluntary resignation", "Involuntary", "End of contract"],
    )

    st.divider()
    st.subheader("Section 2: Role Clarity & Understanding")
    q_role_clarity = rating_question(
        "I had a clear understanding of what was expected of me in my role.", "q_role_clarity"
    )
    q_role_tools = rating_question(
        "I had the tools, information, and training needed to do my job well.", "q_role_tools"
    )
    q_role_match = rating_question(
        "My actual day-to-day work matched what was described when I was hired.", "q_role_match"
    )
    q_role_text = st.text_area(
        "Was there anything about your role that felt unclear or different from what you expected?",
        key="q_role_text",
    )

    st.divider()
    st.subheader("Section 3: Manager Relationship")
    q_mgr_comm = rating_question(
        "My manager communicated clearly and regularly with me.", "q_mgr_comm"
    )
    q_mgr_feedback = rating_question(
        "My manager gave me useful, constructive feedback.", "q_mgr_feedback"
    )
    q_mgr_growth = rating_question(
        "My manager supported my growth and development.", "q_mgr_growth"
    )
    q_mgr_comfort = rating_question(
        "I felt comfortable raising concerns or issues with my manager.", "q_mgr_comfort"
    )
    q_mgr_text = st.text_area(
        "What, if anything, could your manager have done differently to support you better?",
        key="q_mgr_text",
    )

    st.divider()
    st.subheader("Section 4: Workload")
    q_workload_manageable = rating_question(
        "My workload was manageable within normal working hours.", "q_workload_manageable"
    )
    q_workload_balance = rating_question(
        "I was able to maintain a healthy work-life balance.", "q_workload_balance"
    )
    q_workload_deadlines = rating_question(
        "Deadlines and expectations were realistic.", "q_workload_deadlines"
    )
    q_burnout_freq = st.select_slider(
        "How often did you feel overworked or burned out?",
        options=["Never", "Rarely", "Sometimes", "Often", "Always"],
        key="q_burnout_freq",
    )

    st.divider()
    st.subheader("Section 5: Compensation & Benefits")
    q_comp_fair = rating_question(
        "My salary was fair relative to my role and responsibilities.", "q_comp_fair"
    )
    q_comp_market = rating_question(
        "My salary was competitive compared to similar roles in the market.", "q_comp_market"
    )
    q_comp_benefits = rating_question(
        "I was satisfied with the benefits offered (health, leave, retirement, etc.).",
        "q_comp_benefits",
    )
    q_comp_factor = st.radio(
        "Was compensation a significant factor in your decision to leave?",
        ["Yes, primary reason", "Yes, contributing factor", "No", "Not applicable"],
        key="q_comp_factor",
        index=None,
    )

    st.divider()
    st.subheader("Section 6: Culture & Environment")
    q_culture_respect = rating_question(
        "I felt respected and valued as an employee.", "q_culture_respect"
    )
    q_culture_belong = rating_question(
        "I felt a sense of belonging on my team.", "q_culture_belong"
    )
    q_culture_values = rating_question(
        "Leadership's actions matched the company's stated values.", "q_culture_values"
    )
    q_culture_overall = st.radio(
        "I would describe the overall culture as:",
        ["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"],
        key="q_culture_overall",
        index=None,
    )
    q_culture_text = st.text_area(
        "Was there a specific culture or environment issue that influenced your decision to leave?",
        key="q_culture_text",
    )

    st.divider()
    st.subheader("Section 7: Work Location & Flexibility")
    q_location_fit = rating_question(
        "My work arrangement (on-site / hybrid / remote) met my needs.", "q_location_fit"
    )
    q_location_factor = st.radio(
        "Did work location/commute play a role in your decision to leave?",
        ["Yes", "No"],
        key="q_location_factor",
        index=None,
    )
    q_location_text = st.text_area(
        "If yes, briefly explain:", key="q_location_text"
    )

    st.divider()
    st.subheader("Section 8: Overall & Wrap-Up")
    q_primary_reason = st.selectbox(
        "What is the primary reason you are leaving? *",
        [
            "",
            "Compensation/benefits",
            "Career growth/advancement",
            "Manager relationship",
            "Workload/burnout",
            "Culture/environment",
            "Work location/commute/flexibility",
            "Better opportunity elsewhere",
            "Personal reasons",
            "Other",
        ],
    )
    q_primary_reason_other = st.text_input(
        "If Other, please specify:", key="q_primary_reason_other"
    )
    q_enps = st.slider(
        "Would you recommend this company as a place to work to a friend? (0 = Not at all, 10 = Definitely)",
        min_value=0,
        max_value=10,
        value=5,
        key="q_enps",
    )
    q_return = st.radio(
        "Would you consider returning to this company in the future?",
        ["Yes", "Maybe", "No"],
        key="q_return",
        index=None,
    )
    q_retain_text = st.text_area(
        "Is there anything we could have done to retain you?", key="q_retain_text"
    )
    q_other_comments = st.text_area(
        "Any other comments or feedback you'd like to share?", key="q_other_comments"
    )

    submitted = st.form_submit_button("Submit Survey", use_container_width=True)

# ----------------------------
# Handle submission
# ----------------------------
if submitted:
    required_missing = []
    if not department.strip():
        required_missing.append("Department")
    if not job_title.strip():
        required_missing.append("Job title")
    if not tenure:
        required_missing.append("Length of employment")
    if not employment_type:
        required_missing.append("Employment type")
    if not departure_type:
        required_missing.append("Departure type")
    if not q_primary_reason:
        required_missing.append("Primary reason for leaving")

    if required_missing:
        st.error(
            "Please complete the following required fields before submitting: "
            + ", ".join(required_missing)
        )
    else:
        response = {
            "department": department,
            "job_title": job_title,
            "tenure": tenure,
            "employment_type": employment_type,
            "departure_type": departure_type,
            "role_clarity": q_role_clarity,
            "role_tools": q_role_tools,
            "role_match": q_role_match,
            "role_text": q_role_text,
            "mgr_communication": q_mgr_comm,
            "mgr_feedback": q_mgr_feedback,
            "mgr_growth_support": q_mgr_growth,
            "mgr_comfort_raising_concerns": q_mgr_comfort,
            "mgr_text": q_mgr_text,
            "workload_manageable": q_workload_manageable,
            "workload_life_balance": q_workload_balance,
            "workload_deadlines_realistic": q_workload_deadlines,
            "burnout_frequency": q_burnout_freq,
            "comp_fair": q_comp_fair,
            "comp_market_competitive": q_comp_market,
            "comp_benefits_satisfaction": q_comp_benefits,
            "comp_was_factor": q_comp_factor,
            "culture_respect": q_culture_respect,
            "culture_belonging": q_culture_belong,
            "culture_values_alignment": q_culture_values,
            "culture_overall": q_culture_overall,
            "culture_text": q_culture_text,
            "location_fit": q_location_fit,
            "location_was_factor": q_location_factor,
            "location_text": q_location_text,
            "primary_reason": q_primary_reason,
            "primary_reason_other": q_primary_reason_other,
            "enps_recommend_0_10": q_enps,
            "would_return": q_return,
            "retain_text": q_retain_text,
            "other_comments": q_other_comments,
        }

        try:
            supabase = get_supabase_client()
            supabase.table(TABLE_NAME).insert(response).execute()
            st.success("Thank you! Your response has been submitted.")
            st.balloons()
        except Exception as e:
            st.error(
                "Something went wrong saving your response. Please let HR know. "
                f"(Details: {e})"
            )

# ----------------------------
# Optional HR-only view (simple password gate)
# ----------------------------
with st.sidebar:
    st.header("HR Dashboard Access")
    pwd = st.text_input("Enter admin password", type="password")
    admin_pwd = st.secrets.get("ADMIN_PASSWORD", "changeme")
    if pwd and pwd == admin_pwd:
        st.success("Access granted")
        try:
            supabase = get_supabase_client()
            result = supabase.table(TABLE_NAME).select("*").order(
                "created_at", desc=True
            ).execute()
            rows = result.data
            if rows:
                df = pd.DataFrame(rows)
                st.metric("Total responses", len(df))
                st.dataframe(df)
                st.download_button(
                    "Download CSV",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="exit_survey_responses.csv",
                    mime="text/csv",
                )
            else:
                st.info("No responses submitted yet.")
        except Exception as e:
            st.error(f"Could not load responses. (Details: {e})")
