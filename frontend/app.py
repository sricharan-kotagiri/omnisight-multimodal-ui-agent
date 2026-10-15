"""Streamlit dashboard for launching and reviewing OmniSight browser runs."""
from __future__ import annotations

import base64
import binascii
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import streamlit as st

from api_client import ApiClientError, get_run, start_run

APP_DIR = Path(__file__).resolve().parent
DEMO_SCREENSHOT = APP_DIR / "assets" / "demo-screenshot.svg"
TERMINAL_STATUSES = {"completed", "complete", "passed", "success", "failed", "error", "recovered"}

st.set_page_config(page_title="OmniSight QA Dashboard", page_icon="🔭", layout="wide")
st.markdown(
    """
    <style>
      .stApp { background: #f4f7fb; }
      [data-testid="stHeader"] { background: rgba(244, 247, 251, .9); }
      .block-container { max-width: 1240px; padding-top: 2rem; padding-bottom: 3rem; }
      [data-testid="stMetric"], [data-testid="stForm"] {
        background: #fff; border: 1px solid #e2e9f2; border-radius: 14px; padding: 14px 16px;
      }
      .eyebrow { color: #087e8b; font-size: .78rem; font-weight: 700; letter-spacing: .12em; }
      .subtle { color: #617187; }
      div.stButton > button[kind="primary"] { background: #087e8b; border: 0; color: #fff; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)


def demo_result(site_url: str, task: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return {
        "run_id": "demo-001",
        "url": site_url,
        "task": task,
        "status": "recovered",
        "screenshot_path": str(DEMO_SCREENSHOT),
        "failure": {"message": "The original CSS locator did not match an element."},
        "recovery": {"suggestion": "Retry using the accessible button name 'Checkout'.", "confidence": 0.92},
        "actions": [
            {"time": now, "action": "Open target page", "status": "passed", "details": site_url},
            {"time": now, "action": "Find checkout button", "status": "failed", "details": "CSS locator returned no match"},
            {"time": now, "action": "Retry with accessible name", "status": "recovered", "details": "Clicked button named Checkout"},
        ],
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
        st.info("The screenshot path is not accessible to this frontend. Return an image URL or base64 image from the API.")
        return
    st.info("No screenshot was included in this run result.")


def action_rows(actions: Any) -> list[dict[str, str]]:
    if not isinstance(actions, list):
        return []
    rows: list[dict[str, str]] = []
    for item in actions:
        if isinstance(item, str):
            rows.append({"Time": "", "Action": item, "Status": "", "Details": ""})
        elif isinstance(item, dict):
            rows.append({
                "Time": str(item.get("time") or item.get("timestamp") or ""),
                "Action": str(item.get("action") or item.get("name") or item.get("step") or "Action"),
                "Status": str(item.get("status") or ""),
                "Details": str(item.get("details") or item.get("message") or ""),
            })
    return rows


def confidence_score(value: Any) -> float | None:
    raw = value.get("confidence") if isinstance(value, dict) else value
    try:
        score = float(raw)
    except (TypeError, ValueError):
        return None
    if 1 < score <= 100:
        score /= 100
    return score if 0 <= score <= 1 else None


def status_notice(status: str) -> None:
    normalized = status.strip().lower()
    label = status.replace("_", " ").title()
    if normalized in {"passed", "complete", "completed", "success", "recovered"}:
        st.success(f"Status: **{label}**")
    elif normalized in {"failed", "error"}:
        st.error(f"Status: **{label}**")
    elif normalized in {"queued", "running", "pending", "started"}:
        st.info(f"Status: **{label}**")
    else:
        st.warning(f"Status: **{label}**")


if "run_result" not in st.session_state:
    st.session_state.run_result = None
if "run_mode" not in st.session_state:
    st.session_state.run_mode = None
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = os.getenv("OMNISIGHT_API_URL", "http://127.0.0.1:8000")

with st.sidebar:
    st.markdown("## 🔭 OmniSight")
    st.caption("Visual browser QA dashboard")
    mode = st.radio("Connection mode", ["Demo preview", "Live backend"], index=0)
    if mode == "Demo preview":
        st.success("Sample data only")
        st.caption("Preview the dashboard without starting a browser or backend.")
    else:
        st.session_state.api_base_url = st.text_input(
            "FastAPI base URL", value=st.session_state.api_base_url,
            help="For example: http://127.0.0.1:8000",
        )
        st.info("Live mode expects POST /runs and GET /runs/{run_id}.")

st.markdown('<div class="eyebrow">AUTONOMOUS BROWSER QA</div>', unsafe_allow_html=True)
st.title("Run and review a browser check")
st.markdown('<p class="subtle">Start a task, inspect browser evidence, and review any recovery suggestion.</p>', unsafe_allow_html=True)

with st.form("run_form", clear_on_submit=False):
    st.subheader("New automation run")
    url_col, task_col = st.columns([1, 1.5])
    with url_col:
        site_url = st.text_input("Website URL", placeholder="https://example.com")
    with task_col:
        task = st.text_input("Task", placeholder="For example: add an item to the cart and open checkout")
    submitted = st.form_submit_button("Run automation", type="primary")

if submitted:
    parsed = urlparse(site_url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        st.warning("Enter a complete website URL beginning with http:// or https://.")
    elif not task.strip():
        st.warning("Describe the browser task before starting a run.")
    else:
        st.session_state.run_result = None
        st.session_state.run_mode = mode
        try:
            with st.spinner("Starting browser automation..."):
                if mode == "Demo preview":
                    st.session_state.run_result = demo_result(site_url.strip(), task.strip())
                else:
                    st.session_state.run_result = start_run(st.session_state.api_base_url, site_url.strip(), task.strip())
        except ApiClientError as exc:
            st.error(str(exc))

result = st.session_state.run_result
if not result:
    st.info("Enter a URL and task, then select Run automation. Start in Demo preview mode.")
elif not isinstance(result, dict):
    st.error("The run result should be a JSON object.")
else:
    status = str(result.get("status") or "unknown")
    run_id = str(result.get("run_id") or result.get("id") or "Not provided")
    st.divider()
    st.subheader("Latest run")
    status_notice(status)
    if st.session_state.run_mode == "Demo preview":
        st.caption("Demo preview: this run and screenshot are sample data.")

    id_col, target_col = st.columns([1, 2])
    id_col.metric("Run ID", run_id)
    target_col.metric("Target", str(result.get("url") or "See submitted URL"))

    if st.session_state.run_mode == "Live backend" and run_id != "Not provided" and status.lower() not in TERMINAL_STATUSES:
        if st.button("Refresh run status"):
            try:
                with st.spinner("Refreshing run status..."):
                    st.session_state.run_result = get_run(st.session_state.api_base_url, run_id)
                st.rerun()
            except ApiClientError as exc:
                st.error(str(exc))

    image_tab, history_tab, recovery_tab = st.tabs(["Screenshot", "Action history", "Failure and recovery"])
    with image_tab:
        show_screenshot(result)
    with history_tab:
        rows = action_rows(result.get("actions") or result.get("action_history"))
        if rows:
            st.dataframe(rows)
        else:
            st.info("No action history was included in this run result.")
    with recovery_tab:
        failure = result.get("failure") or result.get("error")
        if isinstance(failure, dict):
            failure = failure.get("message") or failure.get("detail") or str(failure)
        if failure:
            st.error(str(failure))
        elif status.lower() in {"failed", "error"}:
            st.warning("The run failed, but the backend did not include failure details.")
        else:
            st.success("No failed action was reported.")

        recovery = result.get("recovery") or result.get("recovery_suggestion")
        if isinstance(recovery, dict):
            suggestion = recovery.get("suggestion") or recovery.get("message") or recovery.get("locator")
        else:
            suggestion = recovery
        if suggestion:
            st.markdown("Recovery suggestion")
            st.write(str(suggestion))
        score = confidence_score(recovery)
        if score is None and result.get("confidence") is not None:
            score = confidence_score(result.get("confidence"))
        if score is not None:
            st.metric("Recovery confidence", f"{score:.0%}")
            st.progress(score)