import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

import db
from browser_tools import open_page, snapshot
from detect_demo import detect
from fix_demo import MAX_TRIES, apply_fix
from github_pr import github_ready, open_fix_pr, read_source
from patcher import PAGE_SOURCES, make_patch
from prompts import FIX_PROMPT, VERIFY_PROMPT
from vlm import ask_vlm

ART = Path("artifacts")


def heal(page, issue, dom, out_dir, before):
    """Ek issue ko fix karne ki koshish (max 3 baar). Result dict wapas karo."""
    oid = issue.get("oid")
    if oid is None:
        return None
    oid = int(oid)
    el = next((e for e in dom["elements"] if e["oid"] == oid), None)
    if el is None:
        return None

    history = ""
    fix, after = {}, None
    for attempt in range(1, MAX_TRIES + 1):
        fix = ask_vlm(
            FIX_PROMPT.format(
                issue=json.dumps(issue), vw=dom["viewport_w"], tag=el["tag"],
                text=el["text"], classes=el["classes"], x=el["x"], y=el["y"],
                wd=el["w"], h=el["h"], opacity=el["opacity"], history=history,
            ),
            [before],
        )
        apply_fix(page, oid, fix["new_classes"], fix.get("inline_css", ""))
        after = out_dir / f"after_{oid}_{attempt}.png"
        new_dom = snapshot(page, after)
        new_el = next(e for e in new_dom["elements"] if e["oid"] == oid)

        verdict = ask_vlm(
            VERIFY_PROMPT.format(
                issue=json.dumps(issue), vw=new_dom["viewport_w"], el=json.dumps(new_el)
            ),
            [before, after],
        )
        if verdict.get("fixed"):
            return {"status": "fixed", "attempts": attempt, "fix": fix, "after": after}

        history += f"\nPrevious attempt FAILED: {fix['new_classes']} -> {verdict.get('reason')}"
        apply_fix(page, oid, el["classes"], "")  # wapas original

    return {"status": "failed", "attempts": MAX_TRIES, "fix": fix, "after": after}


def rel(path):
    return path.relative_to(ART).as_posix() if path else None


def maybe_open_pr(finding_id, run_id, page_name, vp, issue, result, before, pr_cache):
    """Verified fix ke liye PR kholo. Ek hi file + issue type ke liye ek hi PR."""
    rel_path = PAGE_SOURCES[page_name]
    key = (rel_path, issue.get("type"))
    if key in pr_cache:
        url, number = pr_cache[key]
        db.set_pr(finding_id, url, number)
        return
    try:
        original = read_source(rel_path)
        patched, summary = make_patch(rel_path, original, issue, result["fix"])
        url, number = open_fix_pr(
            run_id=run_id, finding_id=finding_id, rel_path=rel_path,
            new_content=patched, issue=issue, attempts=result["attempts"],
            page_name=page_name, viewport=vp, before_img=rel(before),
            after_img=rel(result["after"]), summary=summary,
        )
        pr_cache[key] = (url, number)
        db.set_pr(finding_id, url, number)
        print("PR opened:", url)
    except Exception as e:
        print("PR skipped:", e)  # PR fail hone par poora run nahi rukna chahiye


def run_pipeline(run_id, bug, pages, viewports):
    db.update_run(run_id, "running")
    pr_cache = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for page_name in pages:
                for vp in viewports:
                    print(f"Scanning {page_name} on {vp}")
                    out_dir = ART / "runs" / str(run_id) / f"{page_name}_{vp}"
                    out_dir.mkdir(parents=True, exist_ok=True)

                    page = open_page(browser, bug, vp, page_name)
                    before = out_dir / "before.png"
                    issues, dom = detect(page, vp, page_name, before)

                    for issue in issues[:2]:  # ek page par max 2 issues
                        result = heal(page, issue, dom, out_dir, before)
                        finding_id = db.add_finding(
                            run_id=run_id, page=page_name, viewport=vp,
                            issue_type=issue.get("type"), severity=issue.get("severity"),
                            description=issue.get("description"),
                            fix_json=json.dumps(result["fix"]) if result else None,
                            status=result["status"] if result else "unfixable",
                            attempts=result["attempts"] if result else 0,
                            before_img=rel(before),
                            after_img=rel(result["after"]) if result else None,
                        )
                        if result and result["status"] == "fixed" and github_ready():
                            maybe_open_pr(finding_id, run_id, page_name, vp,
                                          issue, result, before, pr_cache)
                    page.context.close()
            browser.close()
        db.update_run(run_id, "done")
        print("Run complete")
    except Exception as e:
        print("RUN FAILED:", e)
        db.update_run(run_id, "failed", str(e)[:300])


if __name__ == "__main__":
    run_pipeline(
        int(sys.argv[1]),
        sys.argv[2] or None,
        sys.argv[3].split(","),
        sys.argv[4].split(","),
    )