# Employee Exit Survey - Streamlit App

A ready-to-deploy Streamlit form covering: role clarity, manager relationship,
workload, compensation, culture & environment, and work location. Responses
are saved to `exit_survey_responses.csv` and viewable via a password-gated
sidebar dashboard.

## Files
- `app.py` - the Streamlit application
- `requirements.txt` - Python dependencies

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Then open the local URL Streamlit prints (usually http://localhost:8501).

## Deploy to Streamlit Community Cloud (free)
1. Push this folder to a GitHub repo (e.g. `exit-survey-app`), with `app.py`
   and `requirements.txt` at the repo root (or note the subfolder path).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **New app**, select the repo/branch, and set the main file path to
   `app.py`.
4. Click **Deploy**. You'll get a public URL like
   `https://your-app-name.streamlit.app`.

## Setting the admin password
The sidebar "HR Dashboard" is gated by a password so only HR can view/download
raw responses. Set it via Streamlit's secrets manager rather than hardcoding it:

- **Locally:** create `.streamlit/secrets.toml` with:
  ```toml
  ADMIN_PASSWORD = "your-secure-password"
  ```
- **On Streamlit Community Cloud:** go to your app's **Settings > Secrets** and
  add the same line. Do not commit `secrets.toml` to GitHub.

If no secret is set, it falls back to the placeholder `"changeme"` -
make sure to set a real password before sharing the app link with departing
employees.

## Important: data persistence
Streamlit Community Cloud's filesystem is **ephemeral** - the CSV file can be
wiped whenever the app restarts or redeploys (e.g., after a code push or
period of inactivity). This app works fine for testing or low-volume use, but
for production use, replace the CSV read/write logic with a persistent store:

- **Google Sheets** (via `gspread` + a service account) - easiest for HR teams
  already comfortable with Sheets.
- **Airtable** (via their REST API) - good if you want a UI on top too.
- **A hosted database** (Postgres via Supabase, Neon, etc.) - most robust for
  larger organizations or if you'll build reporting on top later.

Happy to wire up any of these if you tell me which one your team already uses.

## Customizing
All questions live inside the `with st.form(...)` block in `app.py`, in the
same order as the original survey document (Section 1-8). Add, remove, or
reword questions there directly - each question's answer is captured in the
`response` dictionary right below the form for saving.
