from pathlib import Path
from .failure_panel import render_failure_panel
from .utils.template_loader import load_template

def render_attempt_header(attempts: list[dict]) -> str:
    total = len(attempts)
    failed = sum(1 for a in attempts if a.get("status") == "FAILED")
    passed = total - failed

    if failed == 0:
        summary = f"Attempts: {total} / {passed} passed"
    else:
        summary = f"Attempts: {total} / {failed} failed"

    return (
        '<div class="attempt-header-meta">'
        f'🔁 {summary}'
        '</div>'
    )


def render_attempt_tabs(attempts):
    template_tabs = load_template("attempt_view_tabs.html")
    template_cards = load_template("attempt_view_cards.html")
    tabs = ""
    cards = ""

    for i, a in enumerate(attempts):
        active = "active" if i == len(attempts) - 1 else ""
        aid = a.get('attempt')
        if not aid:
            continue

        base_dir = a.get('base_dir')
        if not base_dir:
            return ""
        failure_panel_html = render_failure_panel(Path(base_dir), aid) if a.get('status') == "FAILED" else ""

        tabs += template_tabs.replace("{{aid}}", str(aid)).replace("{{active}}", str(active))

        failure_panel = (
            f'<button id="panel-btn-{aid}" type="button" onclick="togglePanel({aid});return false;" class="panel-btn">'
            f'<span class="chevron">▶</span> View Failure Details (Attempt {aid})'
            f'</button>'
            if a.get('status') == 'FAILED' else ''
        )
        cards += (template_cards.replace("{{aid}}", str(aid))
                  .replace("{{active}}", str(active))
                  .replace("{{status_icon}}", "❌ FAILED" if a.get('status') == 'FAILED' else "✅ PASSED")
                  .replace("{{duration}}", str(a.get('duration', '-')))
                  # .replace("{{error}}", str(a.get('error', '-')))
                  # .replace("{{url}}", str(a.get('url', '-')))
                  # .replace("{{screenshot}}", "✔️" if a.get('has_screenshot') else "❌")
                  # .replace("{{video}}", "✔️" if a.get('has_video') else "❌")
                  # .replace("{{trace}}", "✔️" if a.get('has_trace') else "❌")
                  .replace("{{view_failure_panel}}", failure_panel)
                  .replace("{{failure_panel_html}}", str(failure_panel_html)))
    return tabs, cards
