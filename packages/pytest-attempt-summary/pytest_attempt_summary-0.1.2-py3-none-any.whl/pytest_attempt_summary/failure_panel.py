import base64, json
from pathlib import Path
from .utils.template_loader import load_template


def render_failure_panel(base_dir: Path, attempt: int) -> str:
    if not base_dir or not base_dir.exists():
        return ""

    # 加载html模板
    template_failure_panel = load_template("failure_panel.html")
    template_trace_block = load_template("trace_block.html")

    def exists(name):
        return (base_dir / name).exists()

    page_url = (base_dir / "url.txt").read_text(encoding="utf-8") if exists("url.txt") else ""

    screenshot = base_dir / "failure.png"
    screenshot_base64 = base64.b64encode(
            screenshot.read_bytes()
        ).decode("utf-8") if exists("failure.png") else ""

    test_error=(base_dir/"test_failure_errors.txt").read_text(encoding="utf-8") if exists("test_failure_errors.txt") else ""

    browser_console_errors = json.loads((base_dir / "browser_console_errors.json").read_text(encoding="utf-8")) if exists("browser_console_errors.json") else {}
    console_pretty = json.dumps(browser_console_errors, indent=2, ensure_ascii=False) if len(browser_console_errors)>0 else ""

    return (template_failure_panel.replace("{{attempt}}", str(attempt))
            .replace("{{page_url}}", str(page_url))
            .replace("{{console_pretty}}", str(console_pretty))
            .replace("{{test_failure_info}}", str(test_error))
            .replace("{{screenshot_base64}}", str(screenshot_base64))
            .replace("{{trace_block}}", str(template_trace_block)))
