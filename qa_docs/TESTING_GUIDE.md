# OmniSight QA Testing Execution Guide

This guide describes how to run all automated and manual tests for the OmniSight project.

---

## 1. Prerequisites Setup
Ensure the virtual environment is activated and dependencies are installed:
```powershell
# Activate Virtual Environment
D:\omni_venv\Scripts\Activate.ps1

# Verify installed testing tools
pytest --version
playwright --version
```

---

## 2. Running Automated Tests

### A. Run All Test Suites
From the project folder:
```powershell
pytest -v
```

### B. Run API Tests Only
Make sure the backend server is running in a separate terminal:
```powershell
# Terminal 1: Start backend
python -m uvicorn api.main:app --port 8000

# Terminal 2: Run API tests
pytest tests/api -v
```

### C. Run Frontend Client Tests Only
```powershell
pytest tests/frontend -v
```

### D. Run DOM & Validator Unit Tests
```powershell
pytest tests/unit -v
```

### E. Run End-to-End (E2E) Self-Healing Browser Tests
```powershell
pytest tests/e2e -v -s
```

---

## 3. Generating Test Reports
To generate a comprehensive test execution report with output logs:
```powershell
pytest --junitxml=qa_docs/test_results.xml -v
```

---

## 4. Manual Dashboard Testing Checklist
1. Open Streamlit Dashboard (`streamlit run frontend/app.py`).
2. Verify:
   - [ ] Page renders without errors at `http://localhost:8501`.
   - [ ] Sidebar displays backend health status.
   - [ ] Demo Mode "Recovery succeeds" scenario renders green result pill.
   - [ ] Demo Mode "Recovery fails" scenario renders red result pill.
   - [ ] Submitting empty fields triggers form input warnings.
   - [ ] Screenshots in `artifacts/` display cleanly.
