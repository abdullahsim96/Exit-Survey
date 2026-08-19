import streamlit as st
import pandas as pd
from supabase import create_client

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Employee Exit Survey", page_icon="📋", layout="wide")

TABLE_NAME = "exit_survey_responses"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


@st.cache_data(ttl=60)
def load_responses():
    supabase = get_supabase_client()
    result = (
        supabase.table(TABLE_NAME).select("*").order("created_at", desc=True).execute()
    )
    rows = result.data
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df


RATING_LABELS = {
    1: "1 - Strongly Disagree",
    2: "2 - Disagree",
    3: "3 - Neutral",
    4: "4 - Agree",
    5: "5 - Strongly Agree",
}

SECTION_COLUMNS = {
    "Role Clarity": ["role_clarity", "role_tools", "role_match"],
    "Manager": [
        "mgr_communication",
        "mgr_feedback",
        "mgr_growth_support",
        "mgr_comfort_raising_concerns",
    ],
    "Workload": [
        "workload_manageable",
        "workload_life_balance",
        "workload_deadlines_realistic",
    ],
    "Compensation": ["comp_fair", "comp_market_competitive", "comp_benefits_satisfaction"],
    "Culture": ["culture_respect", "culture_belonging", "culture_values_alignment"],
    "Location": ["location_fit"],
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
# Sidebar: HR login (shared by the Analytics tab)
# ----------------------------
with st.sidebar:
    st.header("HR Dashboard Access")
    pwd = st.text_input("Enter admin password", type="password")
    admin_pwd = st.secrets.get("ADMIN_PASSWORD", "changeme")
    if pwd:
        if pwd == admin_pwd:
            st.session_state.authenticated = True
            st.success("Access granted. Open the Analytics Dashboard tab.")
        else:
            st.session_state.authenticated = False
            st.error("Incorrect password.")

# ----------------------------
# Tabs
# ----------------------------
tab_survey, tab_dashboard = st.tabs(["📝 Take Survey", "📊 Analytics Dashboard"])

# ============================================================
# TAB 1: SURVEY
# ============================================================
with tab_survey:
    st.title("📋 Employee Exit Survey")
    st.markdown(
        "Thank you for taking the time to complete this survey. Your honest feedback "
        "helps us understand where we can improve. Responses are kept confidential and "
        "reviewed in aggregate. This should take about **7-10 minutes**."
    )
    st.divider()

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
                load_responses.clear()
            except Exception as e:
                st.error(
                    "Something went wrong saving your response. Please let HR know. "
                    f"(Details: {e})"
                )

# ============================================================
# TAB 2: ANALYTICS DASHBOARD (HR only)
# ============================================================
with tab_dashboard:
    if not st.session_state.authenticated:
        st.info("🔒 Enter the admin password in the sidebar to view the analytics dashboard.")
    else:
        try:
            df = load_responses()
        except Exception as e:
            df = pd.DataFrame()
            st.error(f"Could not load responses. (Details: {e})")

        if df.empty:
            st.info("No responses submitted yet.")
        else:
            st.title("📊 Exit Survey Analytics")

            if st.button("🔄 Refresh data"):
                load_responses.clear()
                st.rerun()

            # ---- Top-line metrics ----
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total responses", len(df))
            avg_enps = df["enps_recommend_0_10"].mean()
            col2.metric("Avg. eNPS (0-10)", f"{avg_enps:.1f}" if pd.notna(avg_enps) else "N/A")
            pct_return = (
                (df["would_return"] == "Yes").sum() / df["would_return"].notna().sum() * 100
                if df["would_return"].notna().sum() > 0
                else 0
            )
            col3.metric("Would return", f"{pct_return:.0f}%")
            pct_voluntary = (
                (df["departure_type"] == "Voluntary resignation").sum() / len(df) * 100
            )
            col4.metric("Voluntary departures", f"{pct_voluntary:.0f}%")

            st.divider()

            # ---- Section averages (the core "where is turnover coming from" view) ----
            st.subheader("Average score by section (1-5 scale)")
            st.caption("Sections below 3.0 are worth digging into first.")
            section_avgs = {}
            for section, cols in SECTION_COLUMNS.items():
                valid_cols = [c for c in cols if c in df.columns]
                section_avgs[section] = df[valid_cols].mean(numeric_only=True).mean()
            section_df = pd.DataFrame(
                {"Section": list(section_avgs.keys()), "Average score": list(section_avgs.values())}
            ).set_index("Section")
            st.bar_chart(section_df)

            low_sections = section_df[section_df["Average score"] < 3.0]
            if not low_sections.empty:
                st.warning(
                    "⚠️ Below 3.0 average: "
                    + ", ".join(f"{s} ({v:.1f})" for s, v in low_sections["Average score"].items())
                )

            st.divider()

            # ---- Primary reason breakdown ----
            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("Primary reason for leaving")
                reason_counts = df["primary_reason"].value_counts()
                st.bar_chart(reason_counts)

            with col_right:
                st.subheader("Overall culture rating")
                culture_counts = df["culture_overall"].value_counts()
                st.bar_chart(culture_counts)

            st.divider()

            # ---- Department breakdown ----
            st.subheader("Average scores by department")
            all_rating_cols = [c for cols in SECTION_COLUMNS.values() for c in cols if c in df.columns]
            dept_df = df.groupby("department")[all_rating_cols].mean(numeric_only=True)
            dept_df["Overall avg"] = dept_df.mean(axis=1)
            dept_df["Responses"] = df.groupby("department").size()
            dept_df = dept_df[["Responses", "Overall avg"]].sort_values("Overall avg")
            st.dataframe(dept_df.style.format({"Overall avg": "{:.2f}"}), use_container_width=True)

            st.divider()

            # ---- Responses over time ----
            st.subheader("Responses over time")
            time_df = df.set_index("created_at").resample("W").size()
            time_df.name = "Responses"
            st.line_chart(time_df)

            st.divider()

            # ---- Burnout frequency ----
            st.subheader("Burnout frequency")
            burnout_order = ["Never", "Rarely", "Sometimes", "Often", "Always"]
            burnout_counts = (
                df["burnout_frequency"].value_counts().reindex(burnout_order).fillna(0)
            )
            st.bar_chart(burnout_counts)

            st.divider()

            # ---- Raw data + export ----
            st.subheader("Raw responses")
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "Download CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="exit_survey_responses.csv",
                mime="text/csv",
            )
