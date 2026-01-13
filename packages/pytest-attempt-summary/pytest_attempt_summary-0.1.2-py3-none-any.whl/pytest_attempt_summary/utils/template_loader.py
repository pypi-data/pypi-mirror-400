from importlib.resources import files


def load_template(name: str) -> str:
    return (files("pytest_attempt_summary.templates") / name).read_text(
        encoding="utf-8"
    )


def load_css(name: str) -> str:
    return (files("pytest_attempt_summary.styles") / name).read_text(
        encoding="utf-8"
    )


def load_js(name: str) -> str:
    # path = BASE_DIR / "scripts" / name
    # return path.read_text(encoding="utf-8")
    return (files("pytest_attempt_summary.scripts") / name).read_text(
        encoding="utf-8"
    )
