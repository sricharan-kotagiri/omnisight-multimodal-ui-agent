# Bug Report Template

**Bug ID:** BUG-OMNI-[000]  
**Date Reported:** YYYY-MM-DD  
**Reported By:** [Your Name / QA Intern]  
**Component:** [Frontend Dashboard | Backend API | Self-Healing Agent | Playwright]  
**Severity:** [Critical | Major | Minor | Cosmetic]  
**Priority:** [P1 - Immediate | P2 - High | P3 - Normal]  

---

### 1. Summary / Title
*(A concise, one-line explanation of the issue)*  
*Example: [API] POST /recover returns 500 instead of 422 when URL parameter is missing scheme.*

---

### 2. Environment Details
- **OS:** Windows 10/11
- **Python Version:** 3.11.x
- **Browser:** Chromium (Playwright headless/headed)
- **FastAPI / Uvicorn URL:** `http://127.0.0.1:8000`
- **Dashboard URL:** `http://localhost:8501`

---

### 3. Pre-conditions
- Backend is running (`python -m uvicorn api.main:app`).
- Gemini API key is configured in `.env`.

---

### 4. Steps to Reproduce
1. Open the Streamlit dashboard at `http://localhost:8501`.
2. Switch execution mode to "Live backend".
3. In the "Website address" field, enter `invalid-url`.
4. In the "Failed locator" field, enter `#some-btn`.
5. Click "Recover locator".

---

### 5. Expected Result
*(What should happen according to the specification)*  
*Example: The system should display a friendly input validation error warning the user to enter a valid URL beginning with `http://` or `https://`.*

---

### 6. Actual Result
*(What actually happened)*  
*Example: An unhandled exception alert is rendered on screen with a raw stack trace.*

---

### 7. Logs & Screenshots
- **Terminal Error:**
```text
(Paste error logs / stack traces here)
```
- **Screenshot:** `artifacts/bug_screenshots/...`

---

### 8. Suggested Fix / Recommendations
*(Optional suggestion for the developer)*  
*Example: Add client-side URL regex validation in `api_client.py` before making the network request.*
