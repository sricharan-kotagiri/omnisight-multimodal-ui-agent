"""
Healing API endpoints — v1.

Routes:
  POST /healing/analyze    Analyse a UI failure using AI (Phase 4 stub)
"""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.healing import HealingAnalyzeRequest, HealingAnalyzeResponse

router = APIRouter()


@router.post("/analyze", response_model=HealingAnalyzeResponse)
async def analyze_healing(payload: HealingAnalyzeRequest) -> HealingAnalyzeResponse:
    """
    Analyse a UI failure and suggest an alternative locator.

    PHASE 2 STUB: Gemini integration is not yet connected.
    Phase 4 will replace this stub with real AI analysis:
    - Send screenshot + DOM + context to Gemini
    - Parse and validate the structured JSON response
    - Return the suggested locator with confidence score
    """
    return HealingAnalyzeResponse(
        suggested_locator=None,
        confidence=None,
        reasoning="AI integration not yet connected (Phase 4)",
        model_version="stub",
        raw_response={},
    )
