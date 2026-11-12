import difflib
import json

from prompts import PATCH_PROMPT
from vlm import ask_vlm

# Page ka naam -> repo ke andar uski source file
PAGE_SOURCES = {
    "home": "demo-shop/src/pages/Home.jsx",
    "cart": "demo-shop/src/pages/Cart.jsx",
    "checkout": "demo-shop/src/pages/Checkout.jsx",
}

MAX_CHANGED_LINES = 12


def make_patch(rel_path, original, issue, fix):
    """AI se patched file lo aur check karo ki wo chhoti aur safe hai."""
    result = ask_vlm(
        PATCH_PROMPT.format(
            path=rel_path, issue=json.dumps(issue), fix=json.dumps(fix), source=original
        )
    )
    patched = result.get("patched_file")

    if not isinstance(patched, str) or not patched.strip():
        raise ValueError("AI ne patched file nahi di")
    if patched == original:
        raise ValueError("Patch mein koi change nahi hai")
    if "export default" not in patched:
        raise ValueError("Patch ne file tod di (export default gayab)")

    changed = sum(
        1
        for line in difflib.ndiff(original.splitlines(), patched.splitlines())
        if line[:2] in ("+ ", "- ")
    )
    if changed > MAX_CHANGED_LINES:
        raise ValueError(f"Patch bahut bada hai ({changed} lines), reject")

    return patched, result.get("summary", "")