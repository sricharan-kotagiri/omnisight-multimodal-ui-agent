"""Streamlit dashboard for OmniSight locator recovery."""
from __future__ import annotations

import base64
import binascii
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import streamlit as st

from api_client import ApiClientError, get_api_paths, get_health, recover_locator

APP_DIR = Path(__file__).resolve().parent
DEMO_SCREENSHOT = APP_DIR / "assets" / "demo-screenshot.svg"

st.set_page_config(page_title="OmniSight Self-Healing Dashboard", page_icon="🔭", layout="wide")
st.markdown(
    """
    <style>
      :root { color-scheme: light; }
      .stApp { background: #f3f6fb; color: #15243a; }
      [data-testid="stHeader"] { background: rgba(243, 246, 251, .92); }
      .block-container { max-width: 1280px; padding: 2.4rem 2.6rem 4rem; }
      [data-testid="stSidebar"] { background: #142338; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
      [data-testid="stSidebar"] label,
      [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #d2ddeb; }
      [data-testid="stSidebar"] h2,
      [data-testid="stSidebar"] h3,
      [data-testid="stSidebar"] h4 { color: #fff; }
      [data-testid="stForm"] {
        background: #fff; border: 1px solid #e2e9f2; border-radius: 18px;
        padding: 1.25rem 1.4rem 1.15rem; box-shadow: 0 12px 35px rgba(25, 45, 75, .045);
      }
      [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #e2e9f2; border-radius: 18px;
        box-shadow: 0 10px 28px rgba(25, 45, 75, .035);
      }
      [data-testid="stTextInputRootElement"] input {
        min-height: 3rem; border-radius: 10px; background: #fbfcfe;
      }
      [data-testid="stTextInputRootElement"] input:focus {
        border-color: #129a96; box-shadow: 0 0 0 2px rgba(18, 154, 150, .14);
      }
      div.stButton > button, button[kind="primaryFormSubmit"] {
        min-height: 2.9rem; border-radius: 10px; font-weight: 700;
        transition: transform .15s ease, box-shadow .15s ease;
      }
      div.stButton > button[kind="primary"], button[kind="primaryFormSubmit"] {
        background: #087f82; border: 0; color: #fff;
        box-shadow: 0 5px 14px rgba(8, 127, 130, .18);
      }
      div.stButton > button[kind="primary"]:hover,
      button[kind="primaryFormSubmit"]:hover { background: #066d70; transform: translateY(-1px); }
      [data-testid="stAlert"] { border-radius: 12px; }
      [data-testid="stTabs"] button { font-weight: 650; }
      .brand-lockup { display: flex; align-items: center; gap: .7rem; margin: .2rem 0 1.1rem; }
      .brand-symbol {
        width: 2.35rem; height: 2.35rem; border-radius: .75rem; display: grid;
        place-items: center; color: #fff; font-size: 1.15rem; font-weight: 800;
        background: linear-gradient(145deg, #18b5aa, #087f82);
        box-shadow: 0 8px 18px rgba(8, 127, 130, .24);
      }
      .brand-name { color: #fff; font-size: 1.05rem; font-weight: 750; letter-spacing: .01em; }
      .brand-caption { color: #9cacc1; font-size: .73rem; margin-top: .08rem; }
      .eyebrow { color: #087f82; font-size: .74rem; font-weight: 750; letter-spacing: .15em; text-transform: uppercase; }
      .hero-title { color: #142338; font-size: clamp(2rem, 3.2vw, 2.8rem); font-weight: 760; letter-spacing: -.045em; line-height: 1.12; margin: .35rem 0 .6rem; }
      .hero-copy { max-width: 720px; color: #617187; font-size: 1rem; line-height: 1.65; }
      .mode-card { background: #fff; border: 1px solid #e2e9f2; border-radius: 14px; padding: 1rem 1.1rem; margin-top: .6rem; }
      .mode-card-label { color: #78879b; font-size: .68rem; font-weight: 750; letter-spacing: .11em; text-transform: uppercase; }
      .mode-card-value { color: #17283d; font-size: 1rem; font-weight: 700; margin-top: .32rem; }
      .mode-card-note { color: #718096; font-size: .78rem; margin-top: .2rem; }
      .step-card { height: 100%; background: rgba(255, 255, 255, .72); border: 1px solid #e3eaf3; border-radius: 14px; padding: .9rem 1rem; }
      .step-number { color: #078586; font-size: .68rem; font-weight: 800; letter-spacing: .1em; }
      .step-title { color: #1b2b40; font-size: .91rem; font-weight: 700; margin-top: .28rem; }
      .step-copy { color: #718096; font-size: .77rem; line-height: 1.45; margin-top: .2rem; }
      .section-kicker { color: #087f82; font-size: .7rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
      .result-label { color: #63738a; font-size: .72rem; font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }
      .status-dot { display: inline-block; width: .55rem; height: .55rem; border-radius: 50%; margin-right: .4rem; background: #18a57e; }
      .result-pill { display: inline-block; border-radius: 999px; padding: .34rem .68rem; font-size: .69rem; font-weight: 800; letter-spacing: .08em; }
      .result-pill.success { background: #e5f6ef; color: #08744f; }
      .result-pill.failure { background: #fff0ef; color: #b23b37; }
      .empty-state { border: 1px dashed #cbd6e4; border-radius: 16px; background: rgba(255,255,255,.65); text-align: center; padding: 2.1rem 1rem; }
      .empty-icon { color: #087f82; font-size: 1.55rem; }
      .empty-title { color: #21334b; font-weight: 700; margin-top: .4rem; }
      .empty-copy { color: #718096; font-size: .86rem; margin: .3rem auto 0; max-width: 540px; }
      .subtle { color: #617187; }
      @media (max-width: 700px) {
        .block-container { padding: 1.5rem 1rem 2.5rem; }
        [data-testid="stForm"] { padding: .9rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def demo_result(site_url: str, failed_locator: str, scenario: str) -> dict[str, Any]:
    """Return clearly labelled sample data shaped like the recovery API response."""
    if scenario == "Recovery succeeds":
        replacement = 'get_by_role("button", name="Checkout")'
        return {
            "success": True,
            "message": "Self-healing successful. The replacement locator was validated in the browser.",
            "old_locator": failed_locator,
            "new_locator": replacement,
            "browser_validation": {
                "valid": True,
                "message": "Element is unique, visible and enabled",
                "match_count": 1,
            },
            "recovery_plan": {
                "suggested_locator": replacement,
                "status": "ready_for_browser_retry",
                "validation": {"valid": True},
            },
            "screenshot_path": str(DEMO_SCREENSHOT),
            "demo_scenario": scenario,
            "url": site_url,
        }

    return {
        "success": False,
        "message": "AI locator failed browser validation. Review the page and locator before trying again.",
        "old_locator": failed_locator,
        "new_locator": None,
        "browser_validation": {
            "valid": False,
            "message": "The suggested element could not be verified as unique, visible and enabled.",
            "match_count": 0,
        },
        "recovery_plan": {"status": "validation_failed", "validation": {"valid": False}},
        "screenshot_path": str(DEMO_SCREENSHOT),
        "demo_scenario": scenario,
        "url": site_url,
    }


def show_screenshot(result: dict[str, Any]) -> None:
    screenshot = result.get("screenshot")
    image_url = result.get("screenshot_url")
    image_base64 = result.get("screenshot_base64")
    image_path = result.get("screenshot_path")

    if isinstance(screenshot, dict):
        image_url = screenshot.get("url") or image_url
        image_base64 = screenshot.get("base64") or image_base64
        image_path = screenshot.get("path") or image_path
    elif isinstance(screenshot, str):
        if screenshot.startswith(("http://", "https://")):
            image_url = screenshot
        elif screenshot.startswith("data:image/"):
            image_base64 = screenshot
        elif not image_path:
            image_path = screenshot

    if image_url:
        st.image(image_url)
        return
    if image_base64:
        encoded = str(image_base64)
        if encoded.startswith("data:image/") and "," in encoded:
            encoded = encoded.split(",", 1)[1]
        try:
            st.image(base64.b64decode(encoded, validate=True))
            return
        except (binascii.Error, ValueError):
            st.warning("The backend returned screenshot data that could not be decoded.")
            return
    if image_path:
        path = Path(str(image_path))
        if path.is_file() and path.suffix.lower() == ".svg":
            encoded_svg = base64.b64encode(path.read_bytes()).decode("ascii")
            st.markdown(
                f'<img src="data:image/svg+xml;base64,{encoded_svg}" style="width:100%;height:auto;border-radius:12px" />',
                unsafe_allow_html=True,
            )
            return
        if path.is_file():
            st.image(str(path))
            return
        st.info("The screenshot path is not accessible here. The API can return a screenshot URL or base64 image.")
        return
    st.info("The current recovery response does not include a screenshot.")


def valid_site_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


if "recovery_result" not in st.session_state:
    st.session_state.recovery_result = None
if "recovery_mode" not in st.session_state:
    st.session_state.recovery_mode = None
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = os.getenv("OMNISIGHT_API_URL", "http://127.0.0.1:8000")
if "api_connection" not in st.session_state:
    st.session_state.api_connection = None

live_recovery_available = False

with st.sidebar:
    st.markdown(
        '<div class="brand-lockup"><div class="brand-symbol">O</div><div><div class="brand-name">OmniSight</div><div class="brand-caption">AI self-healing workspace</div></div></div>',
        unsafe_allow_html=True,
    )
    st.divider()
    mode = st.radio("Workspace mode", ["Demo preview", "Live backend"], index=0)

    if mode == "Demo preview":
        demo_scenario = st.selectbox(
            "Preview outcome",
            ["Recovery succeeds", "Recovery fails"],
            help="Show sample recovery responses without calling the API.",
        )
        st.info("Preview mode uses sample data. It does not open a browser or call the API.")
    else:
        st.markdown("#### Backend connection")
        st.session_state.api_base_url = st.text_input(
            "FastAPI base URL",
            value=st.session_state.api_base_url,
            help="For local development: http://127.0.0.1:8000",
        )
        current_api_url = st.session_state.api_base_url.strip().rstrip("/")

        if st.button("Check backend", type="primary", use_container_width=True):
            try:
                health = get_health(current_api_url)
                paths = get_api_paths(current_api_url)
                health_status = str(health.get("status") or "unknown").strip().lower()
                recover_operations = paths.get("/recover", {})
                recover_available = isinstance(recover_operations, dict) and "post" in recover_operations
                st.session_state.api_connection = {
                    "base_url": current_api_url,
                    "health_status": health_status,
                    "recover_available": recover_available,
                    "error": None,
                }
            except ApiClientError as exc:
                st.session_state.api_connection = {
                    "base_url": current_api_url,
                    "health_status": "unavailable",
                    "recover_available": False,
                    "error": str(exc),
                }

        connection = st.session_state.api_connection
        if not connection or connection.get("base_url") != current_api_url:
            st.caption("Check the backend to see its health and available routes.")
        elif connection.get("error"):
            st.error("Could not read the backend status.")
            st.caption(connection["error"])
        else:
            health_status = connection.get("health_status", "unknown")
            if health_status in {"healthy", "active", "ok"}:
                st.success(f"API health: {health_status.title()}")
            else:
                st.warning(f"API responded with: {health_status}")
            live_recovery_available = (
                health_status in {"healthy", "active", "ok"}
                and bool(connection.get("recover_available"))
            )
            if live_recovery_available:
                st.success("POST /recover is ready.")
            else:
                st.warning("Recovery is waiting for POST /recover.")

hero_copy, hero_mode = st.columns([3.4, 1.15])
with hero_copy:
    st.markdown('<div class="eyebrow">OMNISIGHT · AI SELF-HEALING</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">Locator recovery</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-copy">Give OmniSight the page and the Playwright locator that failed. Review the suggested replacement and browser validation in one place.</div>',
        unsafe_allow_html=True,
    )
with hero_mode:
    if mode == "Demo preview":
        mode_value = "Sample data"
        mode_note = "Preview the interface"
    elif live_recovery_available:
        mode_value = "Recovery ready"
        mode_note = "POST /recover available"
    elif (
        st.session_state.api_connection
        and st.session_state.api_connection.get("base_url") == current_api_url
        and st.session_state.api_connection.get("error")
    ):
        mode_value = "Connection issue"
        mode_note = "Check backend address"
    elif (
        st.session_state.api_connection
        and st.session_state.api_connection.get("base_url") == current_api_url
        and st.session_state.api_connection.get("health_status") in {"healthy", "active", "ok"}
    ):
        mode_value = "API connected"
        mode_note = "Waiting for /recover"
    elif st.session_state.api_connection and st.session_state.api_connection.get("base_url") == current_api_url:
        mode_value = "Backend needs attention"
        mode_note = "Review API health"
    else:
        mode_value = "Not checked"
        mode_note = "Check backend in sidebar"
    st.markdown(
        f'<div class="mode-card"><div class="mode-card-label">Current mode</div><div class="mode-card-value">{mode_value}</div><div class="mode-card-note">{mode_note}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")
step_one, step_two, step_three = st.columns(3, gap="medium")
for column, number, title, copy in [
    (step_one, "STEP 01", "Choose a page", "Enter the website where the locator failed."),
    (step_two, "STEP 02", "Share the locator", "Paste the Playwright selector that stopped working."),
    (step_three, "STEP 03", "Review recovery", "Check the replacement and its browser validation."),
]:
    with column:
        st.markdown(
            f'<div class="step-card"><div class="step-number">{number}</div><div class="step-title">{title}</div><div class="step-copy">{copy}</div></div>',
            unsafe_allow_html=True,
        )

st.write("")
with st.container(border=True):
    st.markdown('<div class="section-kicker">New request</div>', unsafe_allow_html=True)
    st.markdown("### Tell us what failed")
    st.caption("These fields match the recovery request accepted by the backend.")
    with st.form("recovery_form", clear_on_submit=False):
        url_col, locator_col = st.columns(2, gap="large")
        with url_col:
            site_url = st.text_input("Website URL", placeholder="https://example.com")
        with locator_col:
            failed_locator = st.text_input(
                "Failed Playwright locator",
                placeholder='button.checkout or get_by_role("button", name="Checkout")',
                help="Paste the locator that did not match or could not be used.",
            )
        if mode == "Live backend" and not live_recovery_available:
            st.caption("Live recovery becomes available when the backend publishes POST /recover.")
        _, action_col = st.columns([2.8, 1])
        with action_col:
            submitted = st.form_submit_button(
                "Recover locator",
                type="primary",
                use_container_width=True,
                disabled=(mode == "Live backend" and not live_recovery_available),
            )

if submitted:
    if not valid_site_url(site_url):
        st.warning("Enter a complete website URL beginning with http:// or https://.")
    elif not failed_locator.strip():
        st.warning("Enter the Playwright locator that failed.")
    else:
        st.session_state.recovery_result = None
        st.session_state.recovery_mode = mode
        try:
            with st.spinner("Requesting locator recovery..."):
                if mode == "Demo preview":
                    st.session_state.recovery_result = demo_result(
                        site_url.strip(), failed_locator.strip(), demo_scenario
                    )
                else:
                    st.session_state.recovery_result = recover_locator(
                        st.session_state.api_base_url,
                        site_url.strip(),
                        failed_locator.strip(),
                    )
        except ApiClientError as exc:
            st.error(str(exc))

result = st.session_state.recovery_result
if not result:
    if mode == "Live backend" and not live_recovery_available:
        st.warning("The backend connection can be checked now. Live recovery will unlock when POST /recover is available.")
    else:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">⌕</div><div class="empty-title">Your recovery result will appear here</div><div class="empty-copy">Submit a recovery request to see the original locator, suggested replacement, browser validation, and any screenshot returned by the API.</div></div>',
            unsafe_allow_html=True,
        )
elif not isinstance(result, dict):
    st.error("The recovery response should be a JSON object.")
else:
    succeeded = bool(result.get("success"))
    st.write("")
    st.markdown('<div class="section-kicker">Latest response</div>', unsafe_allow_html=True)
    with st.container(border=True):
        pill_class = "success" if succeeded else "failure"
        pill_label = "RECOVERED" if succeeded else "NOT RECOVERED"
        st.markdown(
            f'<span class="result-pill {pill_class}">{pill_label}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("### Recovery completed" if succeeded else "### Recovery needs review")
        st.write(str(result.get("message") or ("Replacement locator validated." if succeeded else "No validated replacement was returned.")))
        if st.session_state.recovery_mode == "Demo preview":
            st.caption(f"Demo preview · {result.get('demo_scenario', 'sample result')} · sample data only")

    old_locator = result.get("old_locator") or failed_locator
    new_locator = result.get("new_locator")
    old_col, new_col = st.columns(2, gap="medium")
    with old_col:
        with st.container(border=True):
            st.markdown('<div class="result-label">Original locator</div>', unsafe_allow_html=True)
            st.code(str(old_locator or "Not provided"))
    with new_col:
        with st.container(border=True):
            st.markdown('<div class="result-label">Suggested replacement</div>', unsafe_allow_html=True)
            if new_locator:
                st.code(str(new_locator))
            else:
                st.caption("The backend did not return a replacement locator.")

    validation = result.get("browser_validation")
    if isinstance(validation, dict):
        with st.container(border=True):
            validation_col, count_col = st.columns([3, 1])
            is_valid = validation.get("valid")
            validation_message = validation.get("message") or "No validation message was returned."
            with validation_col:
                st.markdown('<div class="result-label">Browser validation</div>', unsafe_allow_html=True)
                if is_valid is True:
                    st.success(str(validation_message))
                elif is_valid is False:
                    st.warning(str(validation_message))
                else:
                    st.info(str(validation_message))
            with count_col:
                if validation.get("match_count") is not None:
                    st.metric("Matching elements", validation["match_count"])

    screenshot_tab, details_tab = st.tabs(["Screenshot", "Technical details"])
    with screenshot_tab:
        show_screenshot(result)
    with details_tab:
        recovery_plan = result.get("recovery_plan")
        if recovery_plan:
            st.markdown("**Recovery plan**")
            st.json(recovery_plan)
        else:
            st.info("The current recovery response schema does not include a full recovery plan or action history.")
        with st.expander("View complete API response"):
            st.json(result)
