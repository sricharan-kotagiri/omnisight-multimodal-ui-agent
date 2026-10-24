# OmniSight Streamlit Frontend

The dashboard starts browser runs and displays their status, screenshots, action history, failures, and recovery suggestions. Demo preview mode offers successful, failed, and recovered sample runs without calling the backend.

## Run locally from the repository root

    py -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r frontend\requirements.txt
    .\.venv\Scripts\python.exe -m streamlit run frontend\app.py

## Backend contract for Live mode

- POST /runs receives JSON with url and task fields.
- Its response is a JSON object with run_id (or id) and status.
- GET /runs/{run_id} returns the latest run result.
- Optional fields: url, screenshot_url or screenshot_base64, actions (or action_history), failure (or error), and recovery / recovery_suggestion.
- A recovery object may contain suggestion and confidence (0-1 or 0-100).

Agree on endpoint and field names with the backend owner. Update api_client.py if the backend contract differs. Prefer screenshot URLs or base64 image data over backend-local file paths.

Set OMNISIGHT_API_URL to choose the default FastAPI base URL. Keep credentials and .streamlit/secrets.toml out of Git.