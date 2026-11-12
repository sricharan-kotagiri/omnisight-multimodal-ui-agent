from playwright.sync_api import Page

BASE_URL = "http://localhost:5173"

VIEWPORTS = {
    "mobile": {"width": 375, "height": 812},
    "tablet": {"width": 768, "height": 1024},
    "desktop": {"width": 1440, "height": 900},
}

# page ka naam -> (URL path, heading jo screen par aana chahiye)
PAGES = {
    "home": ("/", "Products"),
    "cart": ("/cart", "Your Cart"),
    "checkout": ("/checkout", "Checkout"),
}

# Page ke andar chalne wala JavaScript. Har element ko ek "oid" number deta hai
# taaki AI bata sake ki kaun sa element kharab hai.
EXTRACT_JS = """
() => {
  const out = [];
  const nodes = document.querySelectorAll('button, a, input, h1, h2, p, label');
  nodes.forEach((el, i) => {
    el.setAttribute('data-oid', i);
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    out.push({
      oid: i,
      tag: el.tagName.toLowerCase(),
      text: (el.innerText || el.placeholder || '').trim().slice(0, 60),
      classes: typeof el.className === 'string' ? el.className : '',
      x: Math.round(r.x + window.scrollX), y: Math.round(r.y + window.scrollY),
      w: Math.round(r.width), h: Math.round(r.height),
      opacity: cs.opacity, color: cs.color, bg: cs.backgroundColor,
      visibility: cs.visibility, display: cs.display
    });
  });
  return {
    viewport_w: window.innerWidth,
    scroll_w: document.documentElement.scrollWidth,
    elements: out
  };
}
"""


def open_page(browser, bug, vp_name, page_name):
    path, heading = PAGES[page_name]
    context = browser.new_context(viewport=VIEWPORTS[vp_name])
    page = context.new_page()
    suffix = f"?bug={bug}" if bug and bug != "clean" else ""
    page.goto(f"{BASE_URL}{path}{suffix}")
    page.get_by_role("heading", name=heading, exact=True).wait_for()
    page.wait_for_timeout(300)
    return page


def snapshot(page: Page, shot_path):
    """Screenshot save karo aur DOM ki list wapas do."""
    page.screenshot(path=str(shot_path), full_page=True)
    return page.evaluate(EXTRACT_JS)