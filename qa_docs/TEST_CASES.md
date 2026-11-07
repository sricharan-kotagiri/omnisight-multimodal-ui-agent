# OmniSight Test Case Specification Matrix

| Test ID | Module / Component | Test Scenario / Description | Pre-conditions | Test Steps | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-FE-01** | Frontend UI | Verify empty URL validation on Dashboard form | Dashboard is open at `http://localhost:8501` | 1. Leave URL empty<br>2. Enter locator `#login-btn`<br>3. Click "Recover locator" | Validation message prompts user to enter a valid HTTP/HTTPS URL | High |
| **TC-FE-02** | Frontend UI | Verify invalid URL scheme (e.g. `ftp://` or `example.com`) | Dashboard is open | 1. Enter `ftp://site.com` or `site.com`<br>2. Submit form | Error warning: URL must start with `http://` or `https://` | High |
| **TC-FE-03** | Frontend UI | Verify empty failed locator validation | Dashboard is open | 1. Enter valid URL<br>2. Leave locator empty<br>3. Submit form | Warning: "Enter the Playwright locator that failed" | High |
| **TC-FE-04** | Frontend UI | Verify Demo Mode - "Recovery succeeds" scenario | Dashboard is open | 1. Select "Demo preview mode"<br>2. Choose "Recovery succeeds"<br>3. Click Recover | Green "RECOVERED" badge, replacement locator, and screenshot are rendered | Medium |
| **TC-FE-05** | Frontend UI | Verify Demo Mode - "Recovery fails" scenario | Dashboard is open | 1. Select "Demo preview mode"<br>2. Choose "Recovery fails"<br>3. Click Recover | Red "NOT RECOVERED" badge with failure reasoning displayed | Medium |
| **TC-FE-06** | Frontend UI | Backend health status indicator check | Backend running at port 8000 | 1. Check sidebar backend connection | Green status indicating `GET /health` returned `healthy` | High |
| **TC-FE-07** | Frontend UI | Backend offline graceful degradation | Backend is stopped | 1. Refresh dashboard | UI displays warning that backend is unreachable; does not crash | High |
| **TC-API-01**| Backend API | Verify `GET /` root endpoint | FastAPI server running | 1. Send `GET /` request | HTTP 200 with status: "active" | Medium |
| **TC-API-02**| Backend API | Verify `GET /health` healthcheck endpoint | FastAPI server running | 1. Send `GET /health` request | HTTP 200 with `{"status": "healthy"}` | High |
| **TC-API-03**| Backend API | Verify `POST /recover` with valid payload | FastAPI running, demo site accessible | 1. Send POST with `url` and `failed_locator` | HTTP 200 with `success: true`, `new_locator`, and `browser_validation` | Critical |
| **TC-API-04**| Backend API | Verify `POST /recover` missing locator field | FastAPI server running | 1. Send POST with empty `failed_locator` | HTTP 422 Unprocessable Entity (Pydantic validation error) | High |
| **TC-API-05**| Backend API | Verify `POST /recover` malformed URL | FastAPI server running | 1. Send POST with `url: "not-a-url"` | HTTP 422 Unprocessable Entity (HttpUrl validation error) | High |
| **TC-DOM-01**| Validator | Verify unique CSS selector validation | DOM with single `<button id="btn">` | 1. Validate `#btn` against DOM | Return `valid: True, match_count: 1` | High |
| **TC-DOM-02**| Validator | Verify ambiguous / duplicate locator rejection | DOM with multiple buttons with same class | 1. Validate duplicate locator against DOM | Return `valid: False, match_count: 2`, message: "ambiguous" | High |
| **TC-DOM-03**| Validator | Verify XPath selector validation | DOM with unique element | 1. Validate `//button[@id='btn']` | Return `valid: True, match_count: 1` | Medium |
| **TC-DOM-04**| Validator | Verify non-existent locator handling | Sample HTML DOM | 1. Validate `#missing-btn` | Return `valid: False, match_count: 0` | High |
| **TC-E2E-01**| E2E Flow | End-to-end self-healing on local demo login page | Playwright Chromium installed | 1. Launch `login.html`<br>2. Try broken `#login-btn`<br>3. Trigger self-healing<br>4. Click `#signin-btn` | Broken locator times out, replacement is identified & clicked, success text shown | Critical |
| **TC-E2E-02**| E2E Flow | Verification of screenshot artifact generation | Playwright Chromium installed | 1. Run recovery script | File `artifacts/recovery_screenshot.png` is generated and non-empty | Medium |
| **TC-SEC-01**| Security | Verify `.env` containing `GEMINI_API_KEY` is git-ignored | Git repo directory | 1. Check `.gitignore` for `.env`<br>2. Run `git status` | `.env` is never tracked or staged for commit | Critical |
