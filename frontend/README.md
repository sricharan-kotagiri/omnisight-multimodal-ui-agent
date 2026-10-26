# OmniSight Self-Healing Dashboard

The Streamlit dashboard follows the FastAPI self-healing module. It accepts a website URL and a failed Playwright locator, then displays the backend's recovery result and browser validation. Demo preview mode shows sample success and failure results without calling the API.

## Run locally

From the repository root in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r frontend\requirements.txt
.\.venv\Scripts\python.exe -m streamlit run frontend\app.py
```

The dashboard's default API address is `http://127.0.0.1:8000`. The backend must be running on the same computer for that local address to work. The address can be changed in the dashboard or set with `OMNISIGHT_API_URL`.

The shared light canvas, teal accent, and dark sidebar theme are configured in `.streamlit/config.toml`. The dashboard uses native Streamlit controls so the visual structure stays easy to maintain.

## Current backend integration

The current FastAPI app exposes `GET /` and `GET /health`. The dashboard checks those health and OpenAPI endpoints. It enables live recovery only after FastAPI publishes `POST /recover` in `/openapi.json`.

The backend's declared recovery request is:

```json
{
  "url": "https://example.com",
  "failed_locator": "button.checkout"
}
```

The declared response fields are `success`, `message`, `old_locator`, `new_locator`, and `browser_validation`. The dashboard also displays optional `recovery_plan` and screenshot fields if the endpoint returns them. The current response schema does not declare confidence, action history, or screenshots, so the dashboard does not expect those fields.

The `/recover` route is still being implemented. Until it appears in the OpenAPI document and returns the declared recovery response, use Demo preview mode. The Gemini API key stays in the backend; the frontend does not need or store it.

Open the backend's Swagger page at `http://127.0.0.1:8000/docs` to inspect the routes published by the running API.
