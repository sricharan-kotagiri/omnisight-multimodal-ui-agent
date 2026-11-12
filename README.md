# OmniSight: Multimodal UI Self-Healing QA Agent

OmniSight tests a web app the way a human QA engineer does. It opens the app in a
headless browser, screenshots every page at phone, tablet and desktop sizes, and asks a
vision-language model to find visual bugs that selector-based tests cannot see
(clipped buttons, overlapping text, low contrast, invisible controls).

It then goes further than reporting. It generates a CSS fix, applies it live in the
browser, takes a **new screenshot to verify the fix actually worked** (retrying up to 3
times), turns the verified fix into a source-code patch, and opens a **GitHub Pull Request**
with before/after proof. A QA manager approves or rejects each fix from a React dashboard.

> Built as Project 1 of the Infotact Solutions Advanced Generative AI Engineering programme.

## Why

Traditional end-to-end tests (Selenium, Cypress) depend on hardcoded selectors and cannot judge
visual correctness. A renamed class breaks the test, and a button hanging off the edge of a
phone screen passes every assertion. OmniSight checks what the user actually sees.

## How it works

```
GitHub push
   |  signed webhook
   v
FastAPI gateway ----> SQLite (runs, findings, PR links)
   |
   v
Playwright navigator: Home -> Cart -> Checkout at mobile / tablet / desktop
   |  screenshot + DOM snapshot (positions, opacity, colours)
   v
Vision-language model: detects defects, returns structured JSON
   |
   v
Heal loop (max 3 attempts):
   propose Tailwind fix -> apply live in browser -> new screenshot -> model verifies
   |  verified
   v
Patcher: model rewrites the source file; size and sanity checks reject risky patches
   |
   v
GitHub Pull Request (branch + commit + before/after screenshots)
   |
   v
React dashboard: Approve (merge PR) / Reject (close PR)
```

## Tech stack

| Layer | Technology |
|---|---|
| Target app | React, Vite, Tailwind CSS, React Router (with injectable UI bugs) |
| Browser automation | Playwright for Python (headless Chromium) |
| Vision model | Google Gemini via `google-genai` (swappable client in `vlm.py`) |
| Backend | FastAPI, Uvicorn, SQLite |
| Git integration | PyGithub |
| Dashboard | React, Vite, Tailwind CSS |
| CI and packaging | GitHub Actions, Docker Compose |

## Project structure

```
.
├── demo-shop/              React shop that OmniSight tests (4 injectable bugs)
├── dashboard/              React QA dashboard (port 5174)
├── backend/
│   ├── main.py             FastAPI app: runs API, webhook, approve/reject
│   ├── pipeline.py         Scan -> detect -> heal -> patch -> PR for one run
│   ├── browser_tools.py    Playwright helpers and DOM extraction
│   ├── vlm.py              Gemini client with retries and a mock mode
│   ├── prompts.py          Detect, fix, verify and patch prompts
│   ├── patcher.py          Source patch generation with safety checks
│   ├── github_pr.py        Branch, commit, PR, merge and close
│   ├── db.py               SQLite access
│   ├── detect_demo.py      Run detection on one page from the command line
│   ├── fix_demo.py         Run the detect -> fix -> verify loop on one page
│   ├── evaluate.py         Measure detection precision and recall
│   ├── capture_demo.py     Capture screenshots of every bug variant
│   └── test_webhook.py     Send a correctly signed fake webhook
├── .github/workflows/      GitHub Actions workflow
├── docker-compose.yml
└── start-all.ps1           Start shop, backend and dashboard on Windows
```

## Getting started

### Prerequisites

- Node.js 20 or newer
- Python 3.11 or newer
- Git
- A Gemini API key (https://aistudio.google.com/app/apikey)
- A GitHub fine-grained token for one repo with **Contents** and **Pull requests** set to read and write (only needed for the PR step)

### Install

```bash
# backend
cd backend
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# frontends
cd ../demo-shop  && npm install
cd ../dashboard  && npm install
```

### Configure

Create `backend/.env` (it is git-ignored, never commit it):

```
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3.5-flash
GEMINI_FALLBACK_MODEL=              # optional backup model
WEBHOOK_SECRET=long_random_string   # python -c "import secrets; print(secrets.token_hex(24))"
GITHUB_TOKEN=your_fine_grained_token
GITHUB_REPO=owner/repo
VLM_MODE=mock                       # optional: test the plumbing without calling the model
```

Model names change over time. If you get a "model not found" error, copy a current Flash model name from AI Studio into `GEMINI_MODEL`.

### Run

Windows, one command from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-all.ps1
```

Or with Docker:

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Demo shop | http://localhost:5173 |
| Dashboard | http://localhost:5174 |
| API docs | http://localhost:8000/docs |

## Usage

**From the dashboard:** choose a bug to simulate, pages and screen sizes, then press
**Start run**. Findings appear with before/after screenshots and a link to the Pull Request.
**Approve** merges the PR, **Reject** closes it.

**From the command line:**

```bash
cd backend
python detect_demo.py hidden-button desktop checkout      # find bugs on one page
python fix_demo.py clipped-button mobile checkout         # detect, fix and verify
python evaluate.py                                        # measure accuracy
```

**From CI:** the workflow in `.github/workflows/omnisight.yml` builds the shop on every
push and sends a signed webhook to `/webhook/github`. Add `OMNISIGHT_URL` and
`WEBHOOK_SECRET` as repository secrets.

### API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Health check |
| POST | `/runs` | Start a run (`bug`, `pages`, `viewports`) |
| GET | `/runs`, `/runs/{id}` | List runs, or one run with its findings |
| POST | `/webhook/github` | Signed CI webhook (HMAC SHA-256) |
| POST | `/findings/{id}/approve` | Approve, and merge the PR if there is one |
| POST | `/findings/{id}/reject` | Reject, and close the PR if there is one |

## Injected test bugs

The demo shop turns bugs on with a URL flag, which gives the evaluation a known ground truth.

| Flag | Bug | Where |
|---|---|---|
| `?bug=overlap` | Price text drawn over the product name | Home |
| `?bug=low-contrast` | Light grey price on white | Home |
| `?bug=hidden-button` | "Place order" button has opacity 0 | Checkout |
| `?bug=clipped-button` | Button pushed off the right edge | Checkout (mobile) |

Example: http://localhost:5173/checkout?bug=hidden-button

## Evaluation

Run `python evaluate.py` from `backend/`. It scans 21 cases (4 bugs across 3 screen sizes,
plus 9 clean pages) and prints true and false positives.

| Metric | Result |
|---|---|
| Detection precision | _to be measured_ |
| Detection recall | _to be measured_ |
| Fix verified on first attempt | _to be measured_ |
| Average time per scanned page | _to be measured_ |

## Safety design

- Webhooks are authenticated with an HMAC signature and compared in constant time.
- A patch is rejected if it changes more than 12 lines, is empty, or breaks the file.
- Through a public tunnel only `/` and `/webhook/github` are reachable. Approve and merge are blocked from outside the machine.
- The GitHub token is limited to one repository. Secrets live in `.env`, which is git-ignored.
- Every fix goes through a Pull Request, so a human reviews the diff before anything is merged.

## Limitations

- Fixes are verified visually by the same kind of model that proposed them. There is no full regression suite behind that check.
- The model can miss subtle bugs or raise false positives, which is why approval stays manual.
- Live verification uses inline CSS, because Tailwind only ships classes already used in the source.
- The demo covers one app with a fixed set of flows.
- `VLM_MODE=mock` uses simple rules instead of a model. It tests the plumbing, not detection quality.

## Roadmap

- Crop screenshots to the flagged region to cut tokens and latency
- Local vision model backend (Ollama or LLaVA) alongside Gemini
- Babel-based AST patching of `className` values
- Retry and orchestration with LangGraph
- Run history charts and per-bug accuracy in the dashboard
