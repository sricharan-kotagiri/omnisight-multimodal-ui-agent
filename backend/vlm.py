import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODELS = [
    m
    for m in [os.getenv("GEMINI_MODEL", "gemini-3.5-flash"), os.getenv("GEMINI_FALLBACK_MODEL")]
    if m
]
WAITS = [5, 10, 20, 40, 60]
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def _mock(prompt):
    """Bina AI ke, simple rules se jawab. Sirf plumbing test karne ke liye."""
    if "Find real VISUAL defects" in prompt:
        dom = json.loads(prompt.split("DOM:\n", 1)[1])
        vw = dom["viewport_w"]
        issues = []
        for e in dom["elements"]:
            if float(e["opacity"]) == 0:
                issues.append({"id": "issue-1", "type": "hidden_element", "severity": "high",
                               "description": f"'{e['text']}' has opacity 0", "oid": e["oid"]})
            elif e["x"] + e["w"] > vw + 1:
                issues.append({"id": "issue-1", "type": "clipping", "severity": "high",
                               "description": f"'{e['text']}' goes outside the viewport", "oid": e["oid"]})
        return {"issues": issues}
    if "fixing a Tailwind" in prompt:
        classes = re.search(r'current classes="([^"]*)"', prompt).group(1)
        keep = [c for c in classes.split()
                if c not in ("opacity-0", "relative") and not c.startswith("left-")]
        return {"explanation": "mock: broken classes removed",
                "new_classes": " ".join(keep), "inline_css": "opacity:1;left:0;"}
    if "SOURCE_START" in prompt:
        src = prompt.split("SOURCE_START\n", 1)[1].rsplit("\nSOURCE_END", 1)[0]
        if "hidden_element" in prompt:
            drop = "opacity-0"
        elif '"type": "clipping"' in prompt:
            drop = "left-64"
        else:
            return {"patched_file": src, "summary": "mock: no change"}
        kept = [line for line in src.split("\n") if drop not in line]
        return {"patched_file": "\n".join(kept), "summary": f"mock: removed code containing {drop}"}
    return {"fixed": True, "new_issues": [], "reason": "mock verify"}


def ask_vlm(prompt, image_paths=()):
    """Images + prompt Gemini ko bhejo, JSON (dict) wapas lo."""
    if os.getenv("VLM_MODE") == "mock":
        return _mock(prompt)

    parts = []
    for path in image_paths:
        parts.append(
            types.Part.from_bytes(data=Path(path).read_bytes(), mime_type="image/png")
        )
    parts.append(prompt)

    last_error = None
    for i, wait in enumerate(WAITS):
        model = MODELS[0] if (i < 3 or len(MODELS) == 1) else MODELS[1]
        try:
            response = _get_client().models.generate_content(
                model=model,
                contents=parts,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            text = response.text.strip()
            text = text.removeprefix("```json").removesuffix("```").strip()
            return json.loads(text)
        except Exception as e:
            last_error = e
            print(f"  (try {i + 1}/{len(WAITS)} on {model} failed: {str(e)[:80]}) waiting {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"VLM failed {len(WAITS)} times: {last_error}")