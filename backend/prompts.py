DETECT_PROMPT = """You are a senior QA engineer testing a web page.
Viewport: {vp} ({w}px wide). Page: {page}.

You get a screenshot plus a JSON list of DOM elements. Each element has:
oid (id number), tag, text, classes, x, y, w, h (pixels), opacity, color, bg, visibility, display.

Find real VISUAL defects only:
- clipping: an element goes outside the viewport (x + w is greater than viewport width)
- overlap: text drawn on top of other text
- low_contrast: text that is hard to read against its background
- hidden_element: a control a user needs is invisible (opacity 0, visibility hidden) or not visible in the screenshot
- overflow: the page scrolls sideways

If there are no defects, return {{"issues": []}}.
Return ONLY JSON in this shape:
{{"issues": [{{"id": "issue-1", "type": "clipping", "severity": "high", "description": "what is wrong and where", "oid": 12}}]}}
Use the oid of the single most relevant element (or null).

DOM:
{dom}
"""

FIX_PROMPT = """You are a frontend engineer fixing a Tailwind CSS bug.
Issue: {issue}
Viewport width: {vw}px.
Target element: <{tag}> text="{text}" current classes="{classes}"
Position now: x={x}, y={y}, width={wd}, height={h}, opacity={opacity}
{history}
Return ONLY JSON:
{{"explanation": "short reason", "new_classes": "full replacement class string for this element", "inline_css": "plain CSS declarations with the same effect, for example opacity:1;"}}
Change as little as possible."""

VERIFY_PROMPT = """You are a QA engineer. Image 1 is BEFORE and image 2 is AFTER a CSS fix.
Original issue: {issue}
Viewport width: {vw}px. The fixed element after the fix: {el}
Decide if the issue is fully fixed and no new visual defect was introduced.
Return ONLY JSON: {{"fixed": true, "new_issues": [], "reason": "short reason"}}"""


PATCH_PROMPT = """You are a frontend engineer. A UI bug was found by a visual test and fixed live in the browser.
Make the SAME fix permanent in the source file.

File path: {path}
Issue: {issue}
Live fix that worked in the browser: {fix}

Notes: this demo page shows some bugs only when a URL flag like ?bug=clipped-button is set.
Remove the buggy code path or class so the element ends up with the fixed classes.
Change as few lines as possible and change nothing else.

Return ONLY JSON: {{"patched_file": "the complete new file content", "summary": "one line"}}

SOURCE_START
{source}
SOURCE_END"""