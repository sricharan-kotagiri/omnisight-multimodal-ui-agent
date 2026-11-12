import hashlib
import hmac
import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import db
from github_pr import close_pr, github_ready, merge_pr
from browser_tools import PAGES, VIEWPORTS

load_dotenv()
db.init_db()
db.migrate()
Path("artifacts/runs").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="OmniSight")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)  # dev ke liye khula; production mein sirf dashboard ka URL rakhna
app.mount("/artifacts", StaticFiles(directory="artifacts"), name="artifacts")

KNOWN_BUGS = {None, "overlap", "low-contrast", "hidden-button", "clipped-button"}


class RunRequest(BaseModel):
    commit_sha: str = "manual"
    bug: str | None = None
    pages: list[str] = ["home", "cart", "checkout"]
    viewports: list[str] = ["mobile", "desktop"]


def start_run(commit_sha, bug, pages, viewports):
    if bug not in KNOWN_BUGS:
        raise HTTPException(400, f"Unknown bug '{bug}'")
    if not set(pages) <= set(PAGES) or not set(viewports) <= set(VIEWPORTS):
        raise HTTPException(400, "Unknown page or viewport")

    run_id = db.create_run(commit_sha, bug)
    log = open(f"artifacts/runs/{run_id}.log", "w")
    subprocess.Popen(
        [sys.executable, "pipeline.py", str(run_id), bug or "",
         ",".join(pages), ",".join(viewports)],
        stdout=log, stderr=subprocess.STDOUT,
    )
    return run_id


@app.get("/")
def health():
    return {"status": "ok", "app": "OmniSight"}


@app.post("/runs")
def create_run(req: RunRequest):
    run_id = start_run(req.commit_sha, req.bug, req.pages, req.viewports)
    return {"run_id": run_id, "status": "queued"}


@app.get("/runs")
def get_runs():
    return db.list_runs()


@app.get("/runs/{run_id}")
def get_run(run_id: int):
    run = db.get_run(run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    return run


@app.post("/webhook/github")
async def github_webhook(request: Request):
    body = await request.body()
    secret = os.getenv("WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(500, "WEBHOOK_SECRET is not set in .env")

    signature = request.headers.get("X-Hub-Signature-256", "")
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(401, "Bad signature")

    payload = json.loads(body or b"{}")
    sha = payload.get("after") or (payload.get("head_commit") or {}).get("id") or "unknown"
    bug = request.query_params.get("bug")  # build mein bug simulate karne ke liye
    run_id = start_run(sha, bug, ["home", "cart", "checkout"], ["mobile", "desktop"])
    return {"run_id": run_id, "status": "queued"}


def _review(finding_id, value):
    finding = db.get_finding(finding_id)
    if finding is None:
        raise HTTPException(404, "Finding not found")

    # Agar is finding ka PR hai: approve = merge, reject = close
    if finding.get("pr_number") and github_ready():
        try:
            if value == "approved":
                merge_pr(finding["pr_number"])
            else:
                close_pr(finding["pr_number"])
        except Exception as e:
            raise HTTPException(502, f"GitHub error: {e}")

    db.set_review(finding_id, value)
    return {"finding_id": finding_id, "review": value}


@app.post("/findings/{finding_id}/approve")
def approve(finding_id: int):
    return _review(finding_id, "approved")


@app.post("/findings/{finding_id}/reject")
def reject(finding_id: int):
    return _review(finding_id, "rejected")