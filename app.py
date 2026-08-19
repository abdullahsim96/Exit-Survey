import secrets
from datetime import datetime, time as dtime

import streamlit as st
import pandas as pd
from supabase import create_client

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Employee Exit Survey", page_icon="📋", layout="wide")

TABLE_NAME = "exit_survey_responses"
LINKS_TABLE = "survey_links"

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


@st.cache_data(ttl=15)
def get_link(token):
    supabase = get_supabase_client()
    result = supabase.table(LINKS_TABLE).select("*").eq("token", token).execute()
    rows = result.data
    return rows[0] if rows else None


@st.cache_data(ttl=15)
def get_all_links():
    supabase = get_supabase_client()
    result = supabase.table(LINKS_TABLE).select("*").order("created_at", desc=True).execute()
    rows = result.data
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def is_link_expired(link):
    if not link.get("is_active", True):
        return True
    deadline = link.get("deadline")
    if deadline:
        deadline_dt = pd.to_datetime(deadline, utc=True)
        if pd.Timestamp.now(tz="UTC") > deadline_dt:
            return True
    return False


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
}

# ============================================================
# TRANSLATIONS
# Stored DB values always stay in English (canonical) for
# consistent reporting; only the displayed labels change.
# ============================================================

RATING_LABELS = {
    "en": {
        1: "1 - Strongly Disagree",
        2: "2 - Disagree",
        3: "3 - Neutral",
        4: "4 - Agree",
        5: "5 - Strongly Agree",
    },
    "ar": {
        1: "1 - غير موافق بشدة",
        2: "2 - غير موافق",
        3: "3 - محايد",
        4: "4 - موافق",
        5: "5 - موافق بشدة",
    },
}

OPT = {
    "culture_overall": {
        "en": {"Very Positive": "Very Positive", "Positive": "Positive", "Neutral": "Neutral",
               "Negative": "Negative", "Very Negative": "Very Negative"},
        "ar": {"Very Positive": "إيجابية جدًا", "Positive": "إيجابية", "Neutral": "محايدة",
               "Negative": "سلبية", "Very Negative": "سلبية جدًا"},
    },
    "yes_no": {
        "en": {"Yes": "Yes", "No": "No"},
        "ar": {"Yes": "نعم", "No": "لا"},
    },
    "primary_reason": {
        "en": {
            "Compensation/benefits": "Compensation/benefits",
            "Career growth/advancement": "Career growth/advancement",
            "Manager relationship": "Manager relationship",
            "Workload/burnout": "Workload/burnout",
            "Culture/environment": "Culture/environment",
            "Work location/commute/flexibility": "Work location/commute/flexibility",
            "Better opportunity elsewhere": "Better opportunity elsewhere",
            "Personal reasons": "Personal reasons",
            "Other": "Other",
        },
        "ar": {
            "Compensation/benefits": "التعويضات/المزايا",
            "Career growth/advancement": "النمو الوظيفي/الترقية",
            "Manager relationship": "العلاقة مع المدير",
            "Workload/burnout": "عبء العمل/الاحتراق الوظيفي",
            "Culture/environment": "الثقافة/بيئة العمل",
            "Work location/commute/flexibility": "موقع العمل/التنقل/المرونة",
            "Better opportunity elsewhere": "فرصة أفضل في مكان آخر",
            "Personal reasons": "أسباب شخصية",
            "Other": "أخرى",
        },
    },
    "return": {
        "en": {"Yes": "Yes", "Maybe": "Maybe", "No": "No"},
        "ar": {"Yes": "نعم", "Maybe": "ربما", "No": "لا"},
    },
}

T = {
    "en": {
        "title": "📋 Employee Exit Survey",
        "intro": (
            "Thank you for taking the time to complete this survey. Your honest feedback "
            "helps us understand where we can improve. Responses are kept confidential and "
            "reviewed in aggregate. This should take about **5-10 minutes**."
        ),
        "all_required": "All questions are required.",
        "s1_title": "Section 1: Background",
        "department": "Department *",
        "crm": "CRM *",
        "job_title": "Job title *",
        "s2_title": "Section 2: Role Clarity & Understanding",
        "role_clarity": "I had a clear understanding of what was expected of me in my role. *",
        "role_tools": "I had the tools, information, and training needed to do my job well. *",
        "role_match": "My actual day-to-day work matched what was described when I was hired. *",
        "role_text": "Was there anything about your role that felt unclear or different from what you expected? *",
        "s3_title": "Section 3: Manager Relationship (Direct Manager)",
        "mgr_comm": "My direct manager communicated clearly and regularly with me. *",
        "mgr_feedback": "My direct manager gave me useful, constructive feedback. *",
        "mgr_growth": "My direct manager supported my growth and development. *",
        "mgr_comfort": "I felt comfortable raising concerns or issues with my direct manager. *",
        "mgr_text": "What, if anything, could your direct manager have done differently to support you better? *",
        "s4_title": "Section 4: Workload",
        "workload_manageable": "My workload was manageable within normal working hours. *",
        "workload_balance": "I was able to maintain a healthy work-life balance. *",
        "workload_deadlines": "My targets and KPIs were realistic and achievable. *",
        "s5_title": "Section 5: Compensation & Benefits",
        "comp_fair": "My salary was fair relative to my role and responsibilities. *",
        "comp_market": "My salary was competitive compared to similar roles in the market. *",
        "comp_benefits": "I was satisfied with the benefits offered (health, leave, etc.). *",
        "s6_title": "Section 6: Culture & Environment",
        "culture_respect": "I felt respected and valued as an employee. *",
        "culture_belong": "I felt a sense of belonging on my team. *",
        "culture_values": "Leadership's actions matched the company's stated values. *",
        "culture_overall": "I would describe the overall culture as: *",
        "culture_text": "Was there a specific culture or environment issue that influenced your decision to leave? *",
        "s7_title": "Section 7: Work Location & Flexibility",
        "location_factor": "Did work location/commute play a role in your decision to leave? *",
        "location_text": "If yes, briefly explain: (required if yes above)",
        "s8_title": "Section 8: Overall & Wrap-Up",
        "primary_reason": "What is the primary reason you are leaving? *",
        "primary_reason_other": "If Other, please specify: (required if 'Other' selected above)",
        "enps": "Would you recommend this company as a place to work to a friend? (0 = Not at all, 10 = Definitely)",
        "return": "Would you consider returning to this company in the future? *",
        "other_comments": "Any other comments or feedback you'd like to share? *",
        "submit": "Submit Survey",
        "missing_prefix": "Please complete the following required fields before submitting: ",
        "success": "Thank you! Your response has been submitted.",
        "save_error": "Something went wrong saving your response. Please let HR know. (Details: {e})",
        "lang_label": "Language / اللغة",
        "link_invalid": "This survey link is invalid. Please contact HR for the correct link.",
        "link_expired": "This survey link has expired or is no longer accepting responses. Please contact HR.",
    },
    "ar": {
        "title": "📋 استبيان مقابلة إنهاء الخدمة",
        "intro": (
            "شكرًا لك على تخصيص وقتك لإكمال هذا الاستبيان. ملاحظاتك الصادقة تساعدنا على "
            "فهم النقاط التي يمكننا تحسينها. يتم الحفاظ على سرية الإجابات ومراجعتها بشكل "
            "إجمالي. يستغرق إكمال الاستبيان من **5 إلى 10 دقائق** تقريبًا."
        ),
        "all_required": "جميع الأسئلة إلزامية.",
        "s1_title": "القسم 1: المعلومات الأساسية",
        "department": "الإدارة *",
        "crm": "CRM *",
        "job_title": "المسمى الوظيفي *",
        "s2_title": "القسم 2: وضوح الدور والفهم",
        "role_clarity": "كان لدي فهم واضح لما هو متوقع مني في دوري. *",
        "role_tools": "كانت لدي الأدوات والمعلومات والتدريب اللازم للقيام بعملي بشكل جيد. *",
        "role_match": "تطابق عملي اليومي الفعلي مع ما تم وصفه لي عند التعيين. *",
        "role_text": "هل كان هناك أي شيء في دورك شعرت أنه غير واضح أو مختلف عما توقعته؟ *",
        "s3_title": "القسم 3: العلاقة مع المدير المباشر",
        "mgr_comm": "كان مديري المباشر يتواصل معي بوضوح وبانتظام. *",
        "mgr_feedback": "قدم لي مديري المباشر ملاحظات مفيدة وبناءة. *",
        "mgr_growth": "دعم مديري المباشر نموي وتطوري المهني. *",
        "mgr_comfort": "شعرت بالارتياح لإثارة المخاوف أو المشكلات مع مديري المباشر. *",
        "mgr_text": "ما الذي كان بإمكان مديرك المباشر القيام به بشكل مختلف لدعمك بشكل أفضل، إن وجد؟ *",
        "s4_title": "القسم 4: عبء العمل",
        "workload_manageable": "كان عبء عملي يمكن التعامل معه ضمن ساعات العمل العادية. *",
        "workload_balance": "كنت قادرًا على الحفاظ على توازن صحي بين العمل والحياة. *",
        "workload_deadlines": "كانت الأهداف ومؤشرات الأداء (KPIs) الخاصة بي واقعية وقابلة للتحقيق. *",
        "s5_title": "القسم 5: التعويضات والمزايا",
        "comp_fair": "كان راتبي عادلاً بالنسبة لدوري ومسؤولياتي. *",
        "comp_market": "كان راتبي تنافسيًا مقارنة بالأدوار المماثلة في السوق. *",
        "comp_benefits": "كنت راضيًا عن المزايا المقدمة (الصحية، الإجازات، إلخ). *",
        "s6_title": "القسم 6: الثقافة وبيئة العمل",
        "culture_respect": "شعرت بالاحترام والتقدير كموظف. *",
        "culture_belong": "شعرت بالانتماء إلى فريقي. *",
        "culture_values": "تطابقت تصرفات القيادة مع القيم المعلنة للشركة. *",
        "culture_overall": "أصف الثقافة العامة بأنها: *",
        "culture_text": "هل كانت هناك مشكلة محددة تتعلق بالثقافة أو بيئة العمل أثرت على قرارك بالمغادرة؟ *",
        "s7_title": "القسم 7: موقع العمل والمرونة",
        "location_factor": "هل لعب موقع العمل / التنقل دورًا في قرارك بالمغادرة؟ *",
        "location_text": "إذا كانت الإجابة نعم، يرجى التوضيح باختصار: (مطلوب إذا اخترت نعم أعلاه)",
        "s8_title": "القسم 8: الخلاصة العامة",
        "primary_reason": "ما هو السبب الرئيسي لمغادرتك؟ *",
        "primary_reason_other": "إذا اخترت 'أخرى'، يرجى التحديد: (مطلوب إذا تم اختيار 'أخرى' أعلاه)",
        "enps": "هل توصي بهذه الشركة كمكان للعمل لصديق؟ (0 = إطلاقًا، 10 = بالتأكيد)",
        "return": "هل تفكر في العودة للعمل في هذه الشركة مستقبلاً؟ *",
        "other_comments": "هل لديك أي تعليقات أو ملاحظات أخرى تود مشاركتها؟ *",
        "submit": "إرسال الاستبيان",
        "missing_prefix": "يرجى إكمال الحقول المطلوبة التالية قبل الإرسال: ",
        "success": "شكرًا لك! تم إرسال إجابتك بنجاح.",
        "save_error": "حدث خطأ أثناء حفظ إجابتك. يرجى إبلاغ الموارد البشرية. (التفاصيل: {e})",
        "lang_label": "Language / اللغة",
        "link_invalid": "رابط الاستبيان غير صالح. يرجى التواصل مع الموارد البشرية للحصول على الرابط الصحيح.",
        "link_expired": "لم يعد هذا الرابط يقبل الإجابات، حيث انتهت صلاحيته أو تم إيقافه. يرجى التواصل مع الموارد البشرية.",
    },
}


def rating_question(label, key, lang):
    labels = RATING_LABELS[lang]
    return st.radio(
        label,
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: labels[x],
        horizontal=True,
        key=key,
        index=None,
    )


def translated_choice(label, key, option_key, lang, values=None, horizontal=False, default_index=None):
    mapping = OPT[option_key][lang]
    vals = values if values is not None else list(OPT[option_key]["en"].keys())
    return st.radio(
        label,
        options=vals,
        format_func=lambda v: mapping.get(v, v),
        key=key,
        index=default_index,
        horizontal=horizontal,
    )


# ----------------------------
# Sidebar: HR login (shared by Analytics + Links tabs)
# ----------------------------
with st.sidebar:
    st.header("HR Dashboard Access")
    pwd = st.text_input("Enter admin password", type="password")
    admin_pwd = st.secrets.get("ADMIN_PASSWORD", "changeme")
    if pwd:
        if pwd == admin_pwd:
            st.session_state.authenticated = True
            st.success("Access granted.")
        else:
            st.session_state.authenticated = False
            st.error("Incorrect password.")

# ----------------------------
# Tabs
# ----------------------------
tab_survey, tab_dashboard, tab_links = st.tabs(
    ["📝 Take Survey", "📊 Analytics Dashboard", "🔗 Admin: Links"]
)

# ============================================================
# TAB 1: SURVEY
# ============================================================
with tab_survey:
    lang_choice = st.selectbox("Language / اللغة", ["English", "العربية"], key="lang_choice")
    lang = "ar" if lang_choice == "العربية" else "en"
    tr = T[lang]

    if lang == "ar":
        st.markdown(
            """
            <style>
            .main .block-container { direction: rtl; }
            .main .block-container p, .main .block-container label,
            .main .block-container h1, .main .block-container h2,
            .main .block-container h3, .main .block-container span {
                text-align: right;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    # ---- Link / deadline gate ----
    token_param = st.query_params.get("token")
    link_blocked = False
    block_reason = None
    if token_param:
        try:
            link = get_link(token_param)
        except Exception:
            link = None
        if link is None:
            link_blocked = True
            block_reason = "invalid"
        elif is_link_expired(link):
            link_blocked = True
            block_reason = "expired"

    st.title(tr["title"])
    st.markdown(tr["intro"])

    if link_blocked:
        st.error(tr["link_invalid"] if block_reason == "invalid" else tr["link_expired"])
    else:
        st.caption(tr["all_required"])
        st.divider()

        with st.form("exit_survey_form", clear_on_submit=False):

            st.subheader(tr["s1_title"])
            department = st.selectbox(
                tr["department"],
                ["", "SS-Kids", "SS-Adults", "CC& TMK", "Operations", "HR"],
            )
            crm = st.text_input(tr["crm"])
            job_title = st.text_input(tr["job_title"])

            st.divider()
            st.subheader(tr["s2_title"])
            q_role_clarity = rating_question(tr["role_clarity"], "q_role_clarity", lang)
            q_role_tools = rating_question(tr["role_tools"], "q_role_tools", lang)
            q_role_match = rating_question(tr["role_match"], "q_role_match", lang)
            q_role_text = st.text_area(tr["role_text"], key="q_role_text")

            st.divider()
            st.subheader(tr["s3_title"])
            q_mgr_comm = rating_question(tr["mgr_comm"], "q_mgr_comm", lang)
            q_mgr_feedback = rating_question(tr["mgr_feedback"], "q_mgr_feedback", lang)
            q_mgr_growth = rating_question(tr["mgr_growth"], "q_mgr_growth", lang)
            q_mgr_comfort = rating_question(tr["mgr_comfort"], "q_mgr_comfort", lang)
            q_mgr_text = st.text_area(tr["mgr_text"], key="q_mgr_text")

            st.divider()
            st.subheader(tr["s4_title"])
            q_workload_manageable = rating_question(tr["workload_manageable"], "q_workload_manageable", lang)
            q_workload_balance = rating_question(tr["workload_balance"], "q_workload_balance", lang)
            q_workload_deadlines = rating_question(tr["workload_deadlines"], "q_workload_deadlines", lang)

            st.divider()
            st.subheader(tr["s5_title"])
            q_comp_fair = rating_question(tr["comp_fair"], "q_comp_fair", lang)
            q_comp_market = rating_question(tr["comp_market"], "q_comp_market", lang)
            q_comp_benefits = rating_question(tr["comp_benefits"], "q_comp_benefits", lang)

            st.divider()
            st.subheader(tr["s6_title"])
            q_culture_respect = rating_question(tr["culture_respect"], "q_culture_respect", lang)
            q_culture_belong = rating_question(tr["culture_belong"], "q_culture_belong", lang)
            q_culture_values = rating_question(tr["culture_values"], "q_culture_values", lang)
            q_culture_overall = translated_choice(
                tr["culture_overall"], "q_culture_overall", "culture_overall", lang,
                values=["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"],
            )
            q_culture_text = st.text_area(tr["culture_text"], key="q_culture_text")

            st.divider()
            st.subheader(tr["s7_title"])
            q_location_factor = translated_choice(
                tr["location_factor"], "q_location_factor", "yes_no", lang,
                values=["Yes", "No"], horizontal=True,
            )
            q_location_text = st.text_area(tr["location_text"], key="q_location_text")

            st.divider()
            st.subheader(tr["s8_title"])
            reason_opts = [
                "Compensation/benefits", "Career growth/advancement", "Manager relationship",
                "Workload/burnout", "Culture/environment", "Work location/commute/flexibility",
                "Better opportunity elsewhere", "Personal reasons", "Other",
            ]
            reason_labels = OPT["primary_reason"][lang]
            q_primary_reason = st.selectbox(
                tr["primary_reason"],
                [""] + reason_opts,
                format_func=lambda v: reason_labels.get(v, v) if v else "",
            )
            q_primary_reason_other = st.text_input(tr["primary_reason_other"], key="q_primary_reason_other")
            q_enps = st.slider(tr["enps"], min_value=0, max_value=10, value=5, key="q_enps")
            q_return = translated_choice(
                tr["return"], "q_return", "return", lang,
                values=["Yes", "Maybe", "No"], horizontal=True,
            )
            q_other_comments = st.text_area(tr["other_comments"], key="q_other_comments")

            submitted = st.form_submit_button(tr["submit"], use_container_width=True)

        if submitted:
            required_missing = []
            if not department:
                required_missing.append(tr["department"])
            if not crm.strip():
                required_missing.append(tr["crm"])
            if not job_title.strip():
                required_missing.append(tr["job_title"])

            if q_role_clarity is None:
                required_missing.append(tr["role_clarity"])
            if q_role_tools is None:
                required_missing.append(tr["role_tools"])
            if q_role_match is None:
                required_missing.append(tr["role_match"])
            if not q_role_text.strip():
                required_missing.append(tr["role_text"])

            if q_mgr_comm is None:
                required_missing.append(tr["mgr_comm"])
            if q_mgr_feedback is None:
                required_missing.append(tr["mgr_feedback"])
            if q_mgr_growth is None:
                required_missing.append(tr["mgr_growth"])
            if q_mgr_comfort is None:
                required_missing.append(tr["mgr_comfort"])
            if not q_mgr_text.strip():
                required_missing.append(tr["mgr_text"])

            if q_workload_manageable is None:
                required_missing.append(tr["workload_manageable"])
            if q_workload_balance is None:
                required_missing.append(tr["workload_balance"])
            if q_workload_deadlines is None:
                required_missing.append(tr["workload_deadlines"])

            if q_comp_fair is None:
                required_missing.append(tr["comp_fair"])
            if q_comp_market is None:
                required_missing.append(tr["comp_market"])
            if q_comp_benefits is None:
                required_missing.append(tr["comp_benefits"])

            if q_culture_respect is None:
                required_missing.append(tr["culture_respect"])
            if q_culture_belong is None:
                required_missing.append(tr["culture_belong"])
            if q_culture_values is None:
                required_missing.append(tr["culture_values"])
            if not q_culture_overall:
                required_missing.append(tr["culture_overall"])
            if not q_culture_text.strip():
                required_missing.append(tr["culture_text"])

            if not q_location_factor:
                required_missing.append(tr["location_factor"])
            if q_location_factor == "Yes" and not q_location_text.strip():
                required_missing.append(tr["location_text"])

            if not q_primary_reason:
                required_missing.append(tr["primary_reason"])
            if q_primary_reason == "Other" and not q_primary_reason_other.strip():
                required_missing.append(tr["primary_reason_other"])
            if not q_return:
                required_missing.append(tr["return"])
            if not q_other_comments.strip():
                required_missing.append(tr["other_comments"])

            if required_missing:
                st.error(tr["missing_prefix"] + ", ".join(required_missing))
            else:
                response = {
                    "department": department,
                    "crm": crm,
                    "job_title": job_title,
                    "survey_language": lang,
                    "link_token": token_param,
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
                    "comp_fair": q_comp_fair,
                    "comp_market_competitive": q_comp_market,
                    "comp_benefits_satisfaction": q_comp_benefits,
                    "culture_respect": q_culture_respect,
                    "culture_belonging": q_culture_belong,
                    "culture_values_alignment": q_culture_values,
                    "culture_overall": q_culture_overall,
                    "culture_text": q_culture_text,
                    "location_was_factor": q_location_factor,
                    "location_text": q_location_text,
                    "primary_reason": q_primary_reason,
                    "primary_reason_other": q_primary_reason_other,
                    "enps_recommend_0_10": q_enps,
                    "would_return": q_return,
                    "other_comments": q_other_comments,
                }

                try:
                    supabase = get_supabase_client()
                    supabase.table(TABLE_NAME).insert(response).execute()
                    st.success(tr["success"])
                    st.balloons()
                    load_responses.clear()
                except Exception as e:
                    st.error(tr["save_error"].format(e=e))

# ============================================================
# TAB 2: ANALYTICS DASHBOARD (HR only) - kept in English
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

            col1, col2, col3 = st.columns(3)
            col1.metric("Total responses", len(df))
            avg_enps = df["enps_recommend_0_10"].mean()
            col2.metric("Avg. eNPS (0-10)", f"{avg_enps:.1f}" if pd.notna(avg_enps) else "N/A")
            pct_return = (
                (df["would_return"] == "Yes").sum() / df["would_return"].notna().sum() * 100
                if df["would_return"].notna().sum() > 0
                else 0
            )
            col3.metric("Would return", f"{pct_return:.0f}%")

            st.divider()

            st.subheader("Average score by section (1-5 scale)")
            st.caption("Sections below 3.0 are worth digging into first.")
            section_avgs = {}
            for section, cols in SECTION_COLUMNS.items():
                valid_cols = [c for c in cols if c in df.columns]
                if valid_cols:
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

            st.subheader("Average scores by department")
            all_rating_cols = [c for cols in SECTION_COLUMNS.values() for c in cols if c in df.columns]
            dept_df = df.groupby("department")[all_rating_cols].mean(numeric_only=True)
            dept_df["Overall avg"] = dept_df.mean(axis=1)
            dept_df["Responses"] = df.groupby("department").size()
            dept_df = dept_df[["Responses", "Overall avg"]].sort_values("Overall avg")
            st.dataframe(dept_df.style.format({"Overall avg": "{:.2f}"}), use_container_width=True)

            st.divider()

            st.subheader("Responses over time")
            time_df = df.set_index("created_at").resample("W").size()
            time_df.name = "Responses"
            st.line_chart(time_df)

            if "survey_language" in df.columns:
                st.divider()
                st.subheader("Survey language used")
                lang_counts = df["survey_language"].value_counts()
                st.bar_chart(lang_counts)

            st.divider()

            st.subheader("Raw responses")
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "Download CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="exit_survey_responses.csv",
                mime="text/csv",
            )

# ============================================================
# TAB 3: ADMIN - SURVEY LINKS + DEADLINES (HR only)
# ============================================================
with tab_links:
    if not st.session_state.authenticated:
        st.info("🔒 Enter the admin password in the sidebar to manage survey links.")
    else:
        st.title("🔗 Survey Links & Deadlines")
        st.markdown(
            "Generate a unique link with a submission deadline. Share the link with the "
            "employee — after the deadline (or if you deactivate it early), that link will "
            "stop accepting new responses."
        )

        base_url = st.text_input(
            "Your app's public URL",
            value=st.secrets.get("APP_BASE_URL", ""),
            placeholder="https://your-app.streamlit.app",
            help="Used only to build the shareable link shown below.",
        )

        with st.form("create_link_form"):
            label = st.text_input("Label (optional — e.g. employee name or department)")
            col1, col2 = st.columns(2)
            deadline_date = col1.date_input("Deadline date")
            deadline_time = col2.time_input("Deadline time", value=dtime(23, 59))
            create = st.form_submit_button("Generate Link")

        if create:
            token = secrets.token_urlsafe(8)
            deadline_dt = datetime.combine(deadline_date, deadline_time)
            try:
                supabase = get_supabase_client()
                supabase.table(LINKS_TABLE).insert(
                    {
                        "token": token,
                        "label": label or None,
                        "deadline": deadline_dt.isoformat(),
                        "is_active": True,
                    }
                ).execute()
                get_all_links.clear()
                full_link = f"{base_url.rstrip('/')}/?token={token}" if base_url else f"?token={token}"
                st.success("Link created!")
                st.code(full_link)
            except Exception as e:
                st.error(f"Could not create link. (Details: {e})")

        st.divider()
        st.subheader("Existing links")
        try:
            links_df = get_all_links()
        except Exception as e:
            links_df = pd.DataFrame()
            st.error(f"Could not load links. (Details: {e})")

        if links_df.empty:
            st.info("No links created yet.")
        else:
            now_utc = pd.Timestamp.now(tz="UTC")
            links_df["deadline_parsed"] = pd.to_datetime(links_df["deadline"], utc=True, errors="coerce")
            links_df["status"] = links_df.apply(
                lambda r: "Deactivated"
                if not r.get("is_active", True)
                else ("Expired" if pd.notna(r["deadline_parsed"]) and r["deadline_parsed"] < now_utc else "Active"),
                axis=1,
            )
            display_base = base_url.rstrip("/") if base_url else ""
            links_df["url"] = links_df["token"].apply(
                lambda t: f"{display_base}/?token={t}" if display_base else f"?token={t}"
            )
            st.dataframe(
                links_df[["label", "url", "deadline", "status", "created_at"]],
                use_container_width=True,
            )

            active_links = links_df[links_df["status"] == "Active"]
            if not active_links.empty:
                st.caption("Deactivate a link early:")
                for _, row in active_links.iterrows():
                    if st.button(f"Deactivate: {row.get('label') or row['token']}", key=f"deact_{row['id']}"):
                        try:
                            supabase = get_supabase_client()
                            supabase.table(LINKS_TABLE).update({"is_active": False}).eq("id", row["id"]).execute()
                            get_all_links.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not deactivate. (Details: {e})")
