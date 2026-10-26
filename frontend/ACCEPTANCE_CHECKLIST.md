# Frontend Acceptance Checklist

- [ ] Validate an HTTP or HTTPS website URL and a non-empty failed locator.
- [ ] Show backend health from `GET /health`.
- [ ] Detect `POST /recover` from FastAPI's OpenAPI document and keep live recovery disabled until it exists.
- [ ] Send the request fields `url` and `failed_locator` to `POST /recover`.
- [ ] Display recovery success, message, original locator, replacement locator, and browser validation.
- [ ] Display optional recovery plan and screenshot data when the API returns them.
- [ ] Handle API connection errors, HTTP errors, and malformed JSON clearly.
- [ ] Preview sample success and failure responses without a running backend.
- [ ] Review the dashboard layout at desktop and mobile widths.
- [ ] Check text and control contrast with an accessibility checker.
- [ ] Keep backend secrets, including the Gemini API key, out of the frontend.
