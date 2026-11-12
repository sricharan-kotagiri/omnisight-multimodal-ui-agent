import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from browser_tools import open_page, snapshot
from detect_demo import detect
from prompts import FIX_PROMPT, VERIFY_PROMPT
from vlm import ask_vlm

MAX_TRIES = 3


def apply_fix(page, oid, new_classes, inline_css):
    """Fix ko live browser mein element par lagao (sirf test ke liye)."""
    page.eval_on_selector(
        f'[data-oid="{oid}"]',
        "(el, a) => { el.className = a.cls; el.style.cssText = a.css; }",
        {"cls": new_classes, "css": inline_css or ""},
    )


if __name__ == "__main__":
    bug = sys.argv[1] if len(sys.argv) > 1 else "clipped-button"
    vp = sys.argv[2] if len(sys.argv) > 2 else "mobile"
    page_name = sys.argv[3] if len(sys.argv) > 3 else "checkout"

    out = Path("artifacts/fix") / f"{bug}_{vp}_{page_name}"
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = open_page(browser, bug, vp, page_name)

        # 1) Bug dhundo
        before = out / "before.png"
        issues, dom = detect(page, vp, page_name, before)
        if not issues:
            print("AI ko koi issue nahi mila.")
            sys.exit()

        issue = issues[0]
        print("Issue mila:", json.dumps(issue, indent=2))

        oid = issue.get("oid")
        if oid is None:
            print("AI ne element nahi bataya, ruk rahe hain.")
            sys.exit()
        oid = int(oid)
        el = next(e for e in dom["elements"] if e["oid"] == oid)

        # 2) Fix likhwao -> lagao -> verify (max 3 koshish)
        history = ""
        success = False
        for attempt in range(1, MAX_TRIES + 1):
            print(f"\n--- Attempt {attempt} ---")
            fix = ask_vlm(
                FIX_PROMPT.format(
                    issue=json.dumps(issue),
                    vw=dom["viewport_w"],
                    tag=el["tag"],
                    text=el["text"],
                    classes=el["classes"],
                    x=el["x"],
                    y=el["y"],
                    wd=el["w"],
                    h=el["h"],
                    opacity=el["opacity"],
                    history=history,
                ),
                [before],
            )
            print("AI ka fix:", json.dumps(fix, indent=2))

            apply_fix(page, oid, fix["new_classes"], fix.get("inline_css", ""))
            after = out / f"after_{attempt}.png"
            new_dom = snapshot(page, after)
            new_el = next(e for e in new_dom["elements"] if e["oid"] == oid)

            verdict = ask_vlm(
                VERIFY_PROMPT.format(
                    issue=json.dumps(issue), vw=new_dom["viewport_w"], el=json.dumps(new_el)
                ),
                [before, after],
            )
            print("Verify:", json.dumps(verdict, indent=2))

            if verdict.get("fixed"):
                success = True
                (out / "fix.json").write_text(
                    json.dumps({"issue": issue, "element": el, "fix": fix}, indent=2)
                )
                break

            history += f"\nPrevious attempt FAILED: {fix['new_classes']} -> {verdict.get('reason')}"
            apply_fix(page, oid, el["classes"], "")  # element ko wapas original karo

        browser.close()

    print("\nRESULT:", "FIXED" if success else "NOT FIXED after 3 tries")
    print("Images dekho:", out)