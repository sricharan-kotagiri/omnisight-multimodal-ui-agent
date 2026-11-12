import time
from playwright.sync_api import sync_playwright

from browser_tools import open_page
from detect_demo import detect
from pathlib import Path

# Kaun sa bug kahan sach mein hai (ground truth)
BUG_LOCATIONS = {
    ("overlap", "home"): {"mobile", "tablet", "desktop"},
    ("low-contrast", "home"): {"mobile", "tablet", "desktop"},
    ("hidden-button", "checkout"): {"mobile", "tablet", "desktop"},
    ("clipped-button", "checkout"): {"mobile"},
}

# Test cases: (bug, page, viewport, bug_hona_chahiye)
cases = []
for (bug, page_name), vps in BUG_LOCATIONS.items():
    for vp in ["mobile", "tablet", "desktop"]:
        cases.append((bug, page_name, vp, vp in vps))
for page_name in ["home", "cart", "checkout"]:
    for vp in ["mobile", "tablet", "desktop"]:
        cases.append(("clean", page_name, vp, False))

out = Path("artifacts/eval")
out.mkdir(parents=True, exist_ok=True)
tp = fp = fn = tn = 0

with sync_playwright() as p:
    browser = p.chromium.launch()
    for bug, page_name, vp, expected in cases:
        page = open_page(browser, bug, vp, page_name)
        issues, _ = detect(page, vp, page_name, out / f"{bug}_{vp}_{page_name}.png")
        page.context.close()
        found = len(issues) > 0
        tp += found and expected
        fp += found and not expected
        fn += (not found) and expected
        tn += (not found) and not expected
        mark = "OK " if found == expected else "BAD"
        print(f"{mark} bug={bug:15} page={page_name:9} vp={vp:8} expected={expected} found={found}")
        time.sleep(4)  # free API limit se bachne ke liye
    browser.close()

print(f"\nTP={tp} FP={fp} FN={fn} TN={tn}")
if tp + fp:
    print(f"Precision: {tp / (tp + fp):.2f}")
if tp + fn:
    print(f"Recall:    {tp / (tp + fn):.2f}")