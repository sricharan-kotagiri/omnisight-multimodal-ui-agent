import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from browser_tools import open_page, snapshot
from prompts import DETECT_PROMPT
from vlm import ask_vlm


def detect(page, vp_name, page_name, shot_path):
    """Screenshot + DOM lo, AI se bugs ki list maango."""
    dom = snapshot(page, shot_path)
    prompt = DETECT_PROMPT.format(
        vp=vp_name, w=dom["viewport_w"], page=page_name, dom=json.dumps(dom)
    )
    result = ask_vlm(prompt, [shot_path])
    return result.get("issues", []), dom


if __name__ == "__main__":
    bug = sys.argv[1] if len(sys.argv) > 1 else "clean"
    vp = sys.argv[2] if len(sys.argv) > 2 else "mobile"
    page_name = sys.argv[3] if len(sys.argv) > 3 else "checkout"

    out = Path("artifacts/detect")
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = open_page(browser, bug, vp, page_name)
        issues, _ = detect(page, vp, page_name, out / f"{bug}_{vp}_{page_name}.png")
        browser.close()

    print(f"\nBug={bug}  viewport={vp}  page={page_name}")
    print(json.dumps(issues, indent=2))