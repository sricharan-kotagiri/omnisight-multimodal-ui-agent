# QA Test Plan - OmniSight Multimodal UI Agent

**Project:** OmniSight Multimodal UI Agent (Frontend Dashboard & AI Self-Healing Engine)  
**Author:** QA / Testing Team  
**Version:** 1.0.0  
**Date:** October 2026  

---

## 1. Introduction & Objectives
OmniSight is an AI-powered UI automation and self-healing system designed to detect broken browser locators (e.g., `#login-btn`), analyze the page visually using Google Gemini Vision AI and DOM inspection, and automatically recover the failed locator (e.g., `#signin-btn`) to resume test execution without manual intervention.

**Primary QA Goals:**
1. Verify the end-to-end self-healing pipeline under various website failure scenarios.
2. Ensure the Streamlit Frontend Dashboard displays clear status indicators, validation messages, and recovery results.
3. Validate FastAPI backend endpoints (`GET /health`, `POST /recover`) for performance, reliability, and strict schema validation.
4. Guarantee that sensitive credentials (e.g., `GEMINI_API_KEY`) remain secure and are never leaked to frontend or public logs.

---

## 2. Scope of Testing

### In Scope
- **Frontend Dashboard (Streamlit):**
  - Form validations (URL format, locator inputs).
  - Backend connectivity health checks.
  - "Demo preview mode" execution (Success & Failure paths).
  - "Live backend" recovery execution.
  - Screenshot rendering & responsive UI layout.
- **Backend API (FastAPI):**
  - Health check (`GET /health`).
  - Home status (`GET /`).
  - Recovery execution (`POST /recover`).
  - Error handling (422 Unprocessable Entity, 500 Internal Error, connection timeouts).
- **Core AI Self-Healing Engine (Playwright + Gemini Vision):**
  - DOM extraction & parsing (CSS and XPath).
  - Browser element state checks (visibility, enabled state, match count).
  - Gemini Vision AI prompt construction and response parsing.
  - Re-execution / click verification with the healed locator.

### Out of Scope
- Internal performance benchmarks of Google's cloud Gemini model.
- Browser compatibility testing beyond Chromium (Chrome/Edge).

---

## 3. Test Levels & Strategy

```
       / \
      / E2E \       --> Playwright browser tests (Demo site & Live websites)
     /-------\
    /   API   \     --> FastAPI endpoint tests (/health, /recover)
   /-----------\
  /   Frontend  \   --> Streamlit API client & input validation tests
 /---------------\
/   Unit Tests    \ --> DOM validator, regex parser, schemas
-------------------
```

1. **Unit Testing:** Fast tests for pure Python logic (`validator.py`, `recovery.py`, `api_client.py`).
2. **API Integration Testing:** Validating request/response payloads against Pydantic schemas.
3. **E2E Browser Testing:** Headless and headed Playwright runs verifying actual browser clicks and screenshots.
4. **Manual / Exploratory Testing:** Usability, edge cases, accessibility checks on the Streamlit dashboard.

---

## 4. Test Environment & Tools
- **Test Framework:** Pytest 8.x
- **Browser Automation:** Playwright (Chromium)
- **API Testing:** Requests / Pytest fixtures
- **Python Environment:** Python 3.11+
- **Reporting:** Pytest terminal report, Markdown Test Logs

---

## 5. Pass / Fail Criteria
- **Pass:** 
  - 100% of critical path test cases pass (Health check, Self-healing on demo site, Schema validation).
  - No uncaught 500 crashes on invalid user input.
- **Fail:**
  - Locator recovery crashes without a descriptive message.
  - Frontend fails to alert user on API disconnects.
  - Duplicate locators are accepted without ambiguity warning.
