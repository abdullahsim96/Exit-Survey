# Employee Exit Survey - Streamlit App

A ready-to-deploy Streamlit form covering: role clarity, manager relationship,
workload, compensation, culture & environment, and work location. Responses
are saved to a **Supabase** Postgres database (persists across restarts and
redeploys) and viewable via a password-gated sidebar dashboard.

## Files
- `app.py` - the Streamlit application
- `requirements.txt` - Python dependencies
- `supabase_schema.sql` - run this once in Supabase to create the table

## Supabase setup (one-time)
1. Create a project at https://supabase.com.
2. Open the SQL Editor and run the contents of `supabase_schema.sql`.
3. Go to Project Settings > API and copy the **Project URL** and the
   **service_role** secret key.

## Run locally
```bash
pip install -r requirements.txt
```
Create `.streamlit/secrets.toml` (and add it to `.gitignore`):
```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-service-role-key"
ADMIN_PASSWORD = "your-secure-password"
```
Then:
```bash
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

## Setting secrets on Streamlit Community Cloud
Go to your deployed app's **Settings > Secrets** and add all three keys shown
above (`SUPABASE_URL`, `SUPABASE_KEY`, `ADMIN_PASSWORD`). Saving triggers an
automatic restart. Never commit `secrets.toml` to GitHub.

If `ADMIN_PASSWORD` isn't set, it falls back to the placeholder `"changeme"` -
make sure to set a real password before sharing the app link with departing
employees.

## Data persistence
Responses are stored in Supabase Postgres, not on the app's local disk, so
they survive app restarts, redeploys, and code pushes. Row Level Security is
enabled with no public policies, so the data is only reachable via the
service_role key the app uses server-side - never expose that key in
client-side code or a public repo.

## Customizing
All questions live inside the `with st.form(...)` block in `app.py`, in the
same order as the original survey document (Section 1-8). Add, remove, or
reword questions there directly - each question's answer is captured in the
`response` dictionary right below the form for saving.
