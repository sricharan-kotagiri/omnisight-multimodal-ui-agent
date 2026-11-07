"""Shared Pytest fixtures for OmniSight testing."""
import sys
from pathlib import Path
import pytest

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Add frontend to sys.path so api_client can be imported directly
FRONTEND_DIR = PROJECT_ROOT / "frontend"
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))


@pytest.fixture(scope="session")
def base_api_url():
    """Default local FastAPI server URL."""
    return "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def demo_html_uri():
    """Returns local URI of the demo login page."""
    html_path = PROJECT_ROOT / "ai_self_healing" / "demo_site" / "login.html"
    return html_path.resolve().as_uri()


@pytest.fixture
def sample_dom():
    """Returns a clean HTML DOM for unit testing."""
    return """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Test Dashboard</h1>
        <button id="signin-btn" class="primary-btn">Sign In</button>
        <div class="duplicate-item">Item 1</div>
        <div class="duplicate-item">Item 2</div>
    </body>
    </html>
    """
