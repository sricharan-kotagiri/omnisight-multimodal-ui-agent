from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright

from api.models.schemas import RecoveryRequest, RecoveryResponse
from ai_self_healing.self_healing_agent import recover_failed_locator


app = FastAPI(
    title="OmniSight AI Self-Healing API",
    description="AI-powered UI self-healing and browser recovery",
    version="1.0.0"
)


# Allow local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "OmniSight AI Self-Healing API is running!",
        "status": "active"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/recover", response_model=RecoveryResponse)
def recover(request: RecoveryRequest):

    screenshot_path = (
        Path(__file__).resolve().parent.parent
        / "artifacts"
        / f"recovery_{uuid4().hex}.png"
    )

    browser = None

    try:
        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=True
            )

            page = browser.new_page()

            page.goto(
                str(request.url),
                wait_until="domcontentloaded",
                timeout=20000
            )

            result = recover_failed_locator(
                page=page,
                failed_locator=request.failed_locator,
                screenshot_path=str(screenshot_path)
            )

            recovery_plan = result.get("recovery_plan", {})

            browser_validation = result.get(
                "browser_validation"
            )

            if browser_validation is None:
                browser_validation = recovery_plan.get(
                    "validation"
                )

            return {
                "success": result.get("success", False),
                "message": result.get(
                    "message",
                    "Recovery process completed"
                ),
                "old_locator": request.failed_locator,
                "new_locator": (
                    result.get("new_locator")
                    or recovery_plan.get("suggested_locator")
                ),
                "browser_validation": browser_validation
            }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Recovery failed: {str(error)}"
        )

    finally:

        if browser is not None:
            browser.close()