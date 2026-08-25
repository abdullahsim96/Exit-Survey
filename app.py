import os
import secrets
from datetime import datetime, time as dtime

import streamlit as st
import pandas as pd
from supabase import create_client

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Employee Exit Survey", page_icon="📋", layout="wide")

# ----------------------------
# Global font upsize (applies to both the survey and the dashboard)
# ----------------------------
st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-size: 18px; }
    p, span, label, .stMarkdown, .stCaption { font-size: 1rem !important; }
    h1 { font-size: 2.1rem !important; }
    h2 { font-size: 1.7rem !important; }
    h3 { font-size: 1.4rem !important; }
    .stRadio label, .stSelectbox label, .stTextInput label, .stTextArea label,
    .stMultiSelect label, .stDateInput label, .stSlider label {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }
    /* Streamlit nests the actual label text in a <p> tag, which can
       override the parent's font-weight — target it explicitly so the
       question text visibly renders bold, not just the label wrapper. */
    .stRadio > label p, .stSelectbox > label p, .stTextInput > label p,
    .stTextArea > label p, .stMultiSelect > label p, .stDateInput > label p,
    .stSlider > label p,
    div[data-testid="stWidgetLabel"] p {
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    .stRadio div[role="radiogroup"] label p { font-size: 1rem !important; font-weight: 400 !important; }
    .stButton button, .stFormSubmitButton button, .stDownloadButton button {
        font-size: 1.05rem !important;
        padding: 0.6rem 1.2rem !important;
    }
    div[data-testid="stMetricValue"] { font-size: 2rem !important; }
    div[data-testid="stMetricLabel"] { font-size: 1rem !important; }
    .stDataFrame { font-size: 0.95rem !important; }

    /* Section header styling — colored accent bar, tinted background.
       Uses logical properties (inline-start) so it flips correctly for
       Arabic's right-to-left layout instead of always being on the left. */
    h3 {
        border-inline-start: 5px solid #0061FC !important;
        background: #F0F6FF;
        padding: 0.6rem 0.9rem !important;
        border-radius: 6px;
        margin-top: 2rem !important;
    }

    /* Submit button — brand blue, rounded, subtle shadow */
    .stFormSubmitButton button {
        background-color: #0061FC !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0, 97, 252, 0.25);
        transition: transform 0.1s ease, box-shadow 0.1s ease;
    }
    .stFormSubmitButton button:hover {
        box-shadow: 0 4px 12px rgba(0, 97, 252, 0.35);
        transform: translateY(-1px);
    }

    /* Selected radio option pill highlight */
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        background: #F0F6FF;
        border-radius: 6px;
    }

    /* Text inputs / areas — softer border, rounded corners */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px !important;
    }

    hr { margin: 1.8rem 0 !important; opacity: 0.15; }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    "Role Clarity": ["role_clarity", "role_tools", "workload_deadlines_realistic"],
    "Training": ["role_onboard_training", "role_ongoing_training"],
    "Manager": [
        "mgr_communication",
        "mgr_feedback",
        "mgr_growth_support",
        "mgr_comfort_raising_concerns",
    ],
    "Compensation": ["comp_fair", "comp_benefits_satisfaction"],
    "Vendor": ["vendor_support", "vendor_hr_services"],
    "Culture": ["culture_respect", "culture_belonging"],
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
    "recommend": {
        "en": {"Recommend": "Recommend", "Not recommend": "Not recommend", "Prefer not to say": "Prefer not to say"},
        "ar": {"Recommend": "أوصي", "Not recommend": "لا أوصي", "Prefer not to say": "أفضّل عدم الإفصاح"},
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
        "all_required": "Fields marked with * are required.",
        "s1_title": "Section 1: Background",
        "department": "Department *",
        "small_team": "Small Team Name *",
        "crm": "CRM",
        "job_title": "Job title *",
        "s2_title": "Section 2: Role Clarity",
        "role_clarity": "I had a clear understanding of what was expected of me in my role. *",
        "role_tools": "I had the tools and information needed to do my job well. *",
        "workload_deadlines": "I always knew the targets required of me and my rate of achievement toward them each month. *",
        "role_text": "Was there anything about your role that felt unclear or different from what you expected?",
        "s2b_title": "Section 3: Training & Development",
        "role_onboard_training": "I received adequate training during my onboarding to prepare me well for my role. *",
        "role_ongoing_training": "I received the ongoing on-the-job training I needed to perform my role well. *",
        "s3_title": "Section 4: Manager Relationship (Direct Manager)",
        "mgr_comm": "My direct manager communicated clearly and regularly with me. *",
        "mgr_feedback": "My direct manager gave me useful, constructive feedback. *",
        "mgr_growth": "My direct manager supported my growth and development. *",
        "mgr_comfort": "I felt comfortable raising concerns or issues with my direct manager. *",
        "mgr_text": "What, if anything, could your direct manager have done differently to support you better?",
        "s5_title": "Section 5: Compensation & Benefits",
        "comp_fair": "My salary was fair relative to my role and responsibilities. *",
        "comp_benefits": "I was satisfied with the medical insurance benefits offered. *",
        "s6b_title": "Section 6: Vendor Satisfaction",
        "vendor_support": "I always find it easy to get support and communicate with the vendor. *",
        "vendor_hr": "I was satisfied with the HR services provided by the vendor. *",
        "vendor_text": "Any additional comments about your experience with the vendor?",
        "s6_title": "Section 7: Culture & Environment",
        "culture_respect": "I felt respected and valued as an employee. *",
        "culture_belong": "I felt a sense of belonging on my team. *",
        "culture_overall": "I would describe the overall culture as: *",
        "culture_text": "Was there a specific culture or environment issue that influenced your decision to leave?",
        "s8_title": "Section 8: Overall & Wrap-Up",
        "primary_reason": "What is the primary reason you are leaving? *",
        "primary_reason_other": "If Other, please specify:",
        "enps": "Would you recommend this company as a place to work to a friend? *",
        "return": "Would you consider returning to this company in the future? *",
        "other_comments": "Any other comments or feedback you'd like to share?",
        "submit": "Submit Survey",
        "missing_prefix": "Please complete the following required fields before submitting: ",
        "success": "Thank you! Your response has been submitted.",
        "save_error": "Something went wrong saving your response. Please let HR know. (Details: {e})",
        "lang_label": "Language / اللغة",
        "link_invalid": "This survey link is invalid. Please contact HR for the correct link.",
        "link_expired": "This survey link has expired or is no longer accepting responses. Please contact HR.",
    },
    "ar": {
        "title": "📋 Employee Exit Survey",
        "intro": (
            "شكرًا لتخصيص وقتك لإكمال هذا الاستبيان. تساعدنا ملاحظاتك الصادقة على فهم "
            "النقاط التي يمكننا تحسينها فيها. سيتم الحفاظ على سرية إجاباتك ومراجعتها بشكل "
            "إجمالي فقط. يستغرق إكمال الاستبيان من **5 إلى 10 دقائق** تقريبًا."
        ),
        "all_required": "الحقول المشار إليها بعلامة (*) إلزامية.",
        "s1_title": "القسم 1: المعلومات الأساسية",
        "department": "الإدارة *",
        "small_team": "اسم الفريق (Small Team) *",
        "crm": "CRM",
        "job_title": "المسمى الوظيفي *",
        "s2_title": "القسم 2: وضوح الدور",
        "role_clarity": "كان لدي فهم واضح لما هو متوقع مني في دوري. *",
        "role_tools": "توفرت لدي الأدوات والمعلومات اللازمة لأداء عملي بكفاءة. *",
        "workload_deadlines": "كنت دائمًا على معرفة بالأهداف المطلوبة مني ونسبة تحقيقي لها خلال الشهر. *",
        "role_text": "هل كان هناك أي جانب من دورك شعرت أنه غير واضح أو مختلف عمّا توقعته؟",
        "s2b_title": "القسم 3: التدريب والتطوير",
        "role_onboard_training": "حصلت على تدريب كافٍ في بداية عملي ساعدني على فهم دوري بشكل جيد. *",
        "role_ongoing_training": "تلقيت التدريب المستمر أثناء العمل الذي احتجته لأداء دوري بشكل جيد. *",
        "s3_title": "القسم 4: العلاقة مع المدير المباشر",
        "mgr_comm": "كان مديري المباشر يتواصل معي بوضوح وبانتظام. *",
        "mgr_feedback": "قدم لي مديري المباشر ملاحظات مفيدة وبناءة. *",
        "mgr_growth": "دعمني مديري المباشر في نموي وتطوري المهني. *",
        "mgr_comfort": "شعرت بالارتياح عند طرح المخاوف أو المشكلات على مديري المباشر. *",
        "mgr_text": "ما الذي كان بإمكان مديرك المباشر فعله بشكل مختلف لدعمك على نحو أفضل، إن وجد؟",
        "s5_title": "القسم 5: التعويضات والمزايا",
        "comp_fair": "كان راتبي عادلاً بالنسبة لدوري ومسؤولياتي. *",
        "comp_benefits": "كنت راضيًا عن مزايا التأمين الطبي المقدمة. *",
        "s6b_title": "القسم 6: رضا المورد (Vendor)",
        "vendor_support": "أجد دائمًا الدعم اللازم وأتواصل بسهولة مع المورد (Vendor). *",
        "vendor_hr": "كنت راضيًا عن خدمات الموارد البشرية المقدمة من المورد. *",
        "vendor_text": "هل لديك أي تعليقات إضافية حول تجربتك مع المورد؟",
        "s6_title": "القسم 7: الثقافة وبيئة العمل",
        "culture_respect": "شعرت بالاحترام والتقدير كموظف. *",
        "culture_belong": "شعرت بالانتماء إلى فريقي. *",
        "culture_overall": "كيف تصف ثقافة الشركة بشكل عام؟ *",
        "culture_text": "هل كانت هناك مشكلة محددة تتعلق بالثقافة أو بيئة العمل أثرت على قرارك بالمغادرة؟",
        "s8_title": "القسم 8: الخلاصة العامة",
        "primary_reason": "ما هو السبب الرئيسي لمغادرتك؟ *",
        "primary_reason_other": "إذا اخترت 'أخرى'، يرجى التحديد:",
        "enps": "هل توصي بالعمل في هذه الشركة لأحد أصدقائك؟ *",
        "return": "هل تفكر في العودة للعمل في هذه الشركة مستقبلاً؟ *",
        "other_comments": "هل لديك أي تعليقات أو ملاحظات أخرى تود مشاركتها؟",
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
# Admin auth gate (rendered inside the Dashboard/Links tabs only —
# never on the survey page, so employees taking the survey never
# see a password field).
# ----------------------------
def require_admin_auth(widget_key):
    if st.session_state.authenticated:
        return True
    st.subheader("🔒 HR Access Only")
    pwd = st.text_input("Enter admin password", type="password", key=f"pwd_{widget_key}")
    admin_pwd = st.secrets.get("ADMIN_PASSWORD", "changeme")
    if pwd:
        if pwd == admin_pwd:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False

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

    logo_path = "assets/51talk_logo.png"
    if os.path.exists(logo_path):
        logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1])
        with logo_col2:
            st.image(logo_path, width=180)

    if lang == "en":
        st.markdown(
            f"<h1 style='text-align:center; font-size:3.4rem; margin-bottom:0.5rem;'>{tr['title']}</h1>",
            unsafe_allow_html=True,
        )

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
            small_team = st.text_input(tr["small_team"])
            crm = st.text_input(tr["crm"])
            job_title = st.text_input(tr["job_title"])

            st.divider()
            st.subheader(tr["s2_title"])
            q_role_clarity = rating_question(tr["role_clarity"], "q_role_clarity", lang)
            q_role_tools = rating_question(tr["role_tools"], "q_role_tools", lang)
            q_workload_deadlines = rating_question(tr["workload_deadlines"], "q_workload_deadlines", lang)
            q_role_text = st.text_area(tr["role_text"], key="q_role_text")

            st.divider()
            st.subheader(tr["s2b_title"])
            q_role_onboard_training = rating_question(tr["role_onboard_training"], "q_role_onboard_training", lang)
            q_role_ongoing_training = rating_question(tr["role_ongoing_training"], "q_role_ongoing_training", lang)

            st.divider()
            st.subheader(tr["s3_title"])
            q_mgr_comm = rating_question(tr["mgr_comm"], "q_mgr_comm", lang)
            q_mgr_feedback = rating_question(tr["mgr_feedback"], "q_mgr_feedback", lang)
            q_mgr_growth = rating_question(tr["mgr_growth"], "q_mgr_growth", lang)
            q_mgr_comfort = rating_question(tr["mgr_comfort"], "q_mgr_comfort", lang)
            q_mgr_text = st.text_area(tr["mgr_text"], key="q_mgr_text")

            st.divider()
            st.subheader(tr["s5_title"])
            q_comp_fair = rating_question(tr["comp_fair"], "q_comp_fair", lang)
            q_comp_benefits = rating_question(tr["comp_benefits"], "q_comp_benefits", lang)

            st.divider()
            st.subheader(tr["s6b_title"])
            q_vendor_support = rating_question(tr["vendor_support"], "q_vendor_support", lang)
            q_vendor_hr = rating_question(tr["vendor_hr"], "q_vendor_hr", lang)
            q_vendor_text = st.text_area(tr["vendor_text"], key="q_vendor_text")

            st.divider()
            st.subheader(tr["s6_title"])
            q_culture_respect = rating_question(tr["culture_respect"], "q_culture_respect", lang)
            q_culture_belong = rating_question(tr["culture_belong"], "q_culture_belong", lang)
            q_culture_overall = translated_choice(
                tr["culture_overall"], "q_culture_overall", "culture_overall", lang,
                values=["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"],
            )
            q_culture_text = st.text_area(tr["culture_text"], key="q_culture_text")

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
            q_enps = translated_choice(
                tr["enps"], "q_enps", "recommend", lang,
                values=["Recommend", "Not recommend", "Prefer not to say"], horizontal=True,
            )
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
            if not small_team.strip():
                required_missing.append(tr["small_team"])
            if not job_title.strip():
                required_missing.append(tr["job_title"])

            if q_role_clarity is None:
                required_missing.append(tr["role_clarity"])
            if q_role_tools is None:
                required_missing.append(tr["role_tools"])
            if q_role_onboard_training is None:
                required_missing.append(tr["role_onboard_training"])
            if q_role_ongoing_training is None:
                required_missing.append(tr["role_ongoing_training"])

            if q_mgr_comm is None:
                required_missing.append(tr["mgr_comm"])
            if q_mgr_feedback is None:
                required_missing.append(tr["mgr_feedback"])
            if q_mgr_growth is None:
                required_missing.append(tr["mgr_growth"])
            if q_mgr_comfort is None:
                required_missing.append(tr["mgr_comfort"])

            if q_workload_deadlines is None:
                required_missing.append(tr["workload_deadlines"])

            if q_comp_fair is None:
                required_missing.append(tr["comp_fair"])
            if q_comp_benefits is None:
                required_missing.append(tr["comp_benefits"])

            if q_vendor_support is None:
                required_missing.append(tr["vendor_support"])
            if q_vendor_hr is None:
                required_missing.append(tr["vendor_hr"])

            if q_culture_respect is None:
                required_missing.append(tr["culture_respect"])
            if q_culture_belong is None:
                required_missing.append(tr["culture_belong"])
            if not q_culture_overall:
                required_missing.append(tr["culture_overall"])

            if not q_primary_reason:
                required_missing.append(tr["primary_reason"])
            if not q_enps:
                required_missing.append(tr["enps"])
            if not q_return:
                required_missing.append(tr["return"])

            if required_missing:
                st.error(tr["missing_prefix"] + ", ".join(required_missing))
            else:
                response = {
                    "department": department,
                    "small_team": small_team,
                    "crm": crm,
                    "job_title": job_title,
                    "survey_language": lang,
                    "link_token": token_param,
                    "role_clarity": q_role_clarity,
                    "role_tools": q_role_tools,
                    "role_onboard_training": q_role_onboard_training,
                    "role_ongoing_training": q_role_ongoing_training,
                    "role_text": q_role_text,
                    "mgr_communication": q_mgr_comm,
                    "mgr_feedback": q_mgr_feedback,
                    "mgr_growth_support": q_mgr_growth,
                    "mgr_comfort_raising_concerns": q_mgr_comfort,
                    "mgr_text": q_mgr_text,
                    "workload_deadlines_realistic": q_workload_deadlines,
                    "comp_fair": q_comp_fair,
                    "comp_benefits_satisfaction": q_comp_benefits,
                    "vendor_support": q_vendor_support,
                    "vendor_hr_services": q_vendor_hr,
                    "vendor_text": q_vendor_text,
                    "culture_respect": q_culture_respect,
                    "culture_belonging": q_culture_belong,
                    "culture_overall": q_culture_overall,
                    "culture_text": q_culture_text,
                    "primary_reason": q_primary_reason,
                    "primary_reason_other": q_primary_reason_other,
                    "would_recommend": q_enps,
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
    if not require_admin_auth("dashboard"):
        pass
    else:
        try:
            df = load_responses()
        except Exception as e:
            df = pd.DataFrame()
            st.error(f"Could not load responses. (Details: {e})")

        if df.empty:
            st.info("No responses submitted yet.")
        else:
            header_col, refresh_col = st.columns([5, 1])
            header_col.title("📊 Exit Survey Analytics")
            if refresh_col.button("🔄 Refresh", use_container_width=True):
                load_responses.clear()
                st.rerun()

            # ---- Filters (apply to every view below) ----
            with st.container(border=True):
                fcol1, fcol2 = st.columns(2)
                dept_options = sorted(df["department"].dropna().unique().tolist())
                selected_depts = fcol1.multiselect(
                    "Filter by department", dept_options, default=dept_options
                )
                min_date = df["created_at"].min().date()
                max_date = df["created_at"].max().date()
                if min_date < max_date:
                    date_range = fcol2.date_input(
                        "Filter by date range", value=(min_date, max_date),
                        min_value=min_date, max_value=max_date,
                    )
                else:
                    date_range = (min_date, max_date)

            filtered = df[df["department"].isin(selected_depts)] if selected_depts else df.iloc[0:0]
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start, end = date_range
                filtered = filtered[
                    (filtered["created_at"].dt.date >= start) & (filtered["created_at"].dt.date <= end)
                ]
            st.caption(f"Showing {len(filtered)} of {len(df)} total responses.")

            if filtered.empty:
                st.warning("No responses match the current filters.")
            else:
                view_overview, view_departments, view_feedback, view_raw = st.tabs(
                    ["📈 Overview", "🏢 Departments", "💬 Open Feedback", "📋 Raw Data"]
                )

                # ================= OVERVIEW =================
                with view_overview:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Responses", len(filtered))

                    all_rating_cols = [c for cols in SECTION_COLUMNS.values() for c in cols if c in filtered.columns]
                    overall_avg = filtered[all_rating_cols].mean(numeric_only=True).mean() if all_rating_cols else None
                    col2.metric("Overall avg score", f"{overall_avg:.2f}/5" if pd.notna(overall_avg) else "N/A")

                    if "would_recommend" in filtered.columns and filtered["would_recommend"].notna().sum() > 0:
                        answered = filtered[filtered["would_recommend"] != "Prefer not to say"]
                        pct_recommend = (
                            (answered["would_recommend"] == "Recommend").sum() / len(answered) * 100
                            if len(answered) > 0 else 0
                        )
                        col3.metric("Would recommend", f"{pct_recommend:.0f}%")
                    else:
                        col3.metric("Would recommend", "N/A")

                    pct_return = (
                        (filtered["would_return"] == "Yes").sum() / filtered["would_return"].notna().sum() * 100
                        if filtered["would_return"].notna().sum() > 0
                        else 0
                    )
                    col4.metric("Would return", f"{pct_return:.0f}%")

                    st.divider()

                    chart_col, trend_col = st.columns([3, 2])
                    with chart_col:
                        st.subheader("Average score by section")
                        st.caption("Below 3.0 is worth digging into first.")
                        section_avgs = {}
                        for section, cols in SECTION_COLUMNS.items():
                            valid_cols = [c for c in cols if c in filtered.columns]
                            if valid_cols:
                                section_avgs[section] = filtered[valid_cols].mean(numeric_only=True).mean()
                        section_df = pd.DataFrame(
                            {"Section": list(section_avgs.keys()), "Average score": list(section_avgs.values())}
                        ).set_index("Section")
                        st.bar_chart(section_df, height=300)

                        low_sections = section_df[section_df["Average score"] < 3.0]
                        if not low_sections.empty:
                            st.warning(
                                "⚠️ Below 3.0: "
                                + ", ".join(f"{s} ({v:.1f})" for s, v in low_sections["Average score"].items())
                            )

                    with trend_col:
                        st.subheader("Responses over time")
                        time_df = filtered.set_index("created_at").resample("W").size()
                        time_df.name = "Responses"
                        st.line_chart(time_df, height=300)

                    st.divider()
                    rcol1, rcol2 = st.columns(2)
                    with rcol1:
                        st.subheader("Primary reason for leaving")
                        st.bar_chart(filtered["primary_reason"].value_counts())
                    with rcol2:
                        st.subheader("Overall culture rating")
                        st.bar_chart(filtered["culture_overall"].value_counts())

                # ================= DEPARTMENTS =================
                with view_departments:
                    st.subheader("Average scores by department")
                    all_rating_cols = [c for cols in SECTION_COLUMNS.values() for c in cols if c in filtered.columns]
                    dept_df = filtered.groupby("department")[all_rating_cols].mean(numeric_only=True)
                    dept_df["Overall avg"] = dept_df.mean(axis=1)
                    dept_df["Responses"] = filtered.groupby("department").size()
                    dept_df = dept_df[["Responses", "Overall avg"]].sort_values("Overall avg")
                    st.dataframe(
                        dept_df.style.format({"Overall avg": "{:.2f}"}).background_gradient(
                            subset=["Overall avg"], cmap="RdYlGn", vmin=1, vmax=5
                        ),
                        use_container_width=True,
                    )

                    st.divider()
                    st.subheader("Section breakdown per department")
                    section_by_dept = {}
                    for section, cols in SECTION_COLUMNS.items():
                        valid_cols = [c for c in cols if c in filtered.columns]
                        if valid_cols:
                            section_by_dept[section] = filtered.groupby("department")[valid_cols].mean(numeric_only=True).mean(axis=1)
                    st.dataframe(
                        pd.DataFrame(section_by_dept).style.format("{:.2f}").background_gradient(cmap="RdYlGn", vmin=1, vmax=5),
                        use_container_width=True,
                    )

                    if "survey_language" in filtered.columns:
                        st.divider()
                        st.subheader("Survey language used")
                        st.bar_chart(filtered["survey_language"].value_counts())

                # ================= OPEN FEEDBACK =================
                with view_feedback:
                    st.caption("Free-text answers, most recent first — useful for spotting recurring themes.")
                    text_fields = [
                        ("role_text", "Role clarity comments"),
                        ("mgr_text", "Manager feedback"),
                        ("vendor_text", "Vendor comments"),
                        ("culture_text", "Culture/environment comments"),
                        ("primary_reason_other", "Other reason (specified)"),
                        ("other_comments", "Other comments"),
                    ]
                    for col, label in text_fields:
                        if col not in filtered.columns:
                            continue
                        non_empty = filtered[filtered[col].notna() & (filtered[col].str.strip() != "")]
                        if non_empty.empty:
                            continue
                        with st.expander(f"{label} ({len(non_empty)})"):
                            for _, row in non_empty.sort_values("created_at", ascending=False).iterrows():
                                dept = row.get("department", "—")
                                date_str = row["created_at"].strftime("%Y-%m-%d")
                                st.markdown(f"**{dept} · {date_str}**")
                                st.write(row[col])
                                st.markdown("---")

                # ================= RAW DATA =================
                with view_raw:
                    st.subheader("Raw responses")
                    st.dataframe(filtered, use_container_width=True)
                    st.download_button(
                        "Download filtered CSV",
                        data=filtered.to_csv(index=False).encode("utf-8"),
                        file_name="exit_survey_responses.csv",
                        mime="text/csv",
                    )

# ============================================================
# TAB 3: ADMIN - SURVEY LINKS + DEADLINES (HR only)
# ============================================================
with tab_links:
    if not require_admin_auth("links"):
        pass
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
