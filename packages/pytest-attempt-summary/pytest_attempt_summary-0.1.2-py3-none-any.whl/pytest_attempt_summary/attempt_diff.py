from .utils.template_loader import load_template


def calculate_attempt_diff(attempts: list[dict]) -> str:
    """
    Calculate differences across multiple attempts.
    Only shows dimensions that actually differ.
    """
    template_attempt_diff = load_template("attempt_diff.html")
    diff_blocks = []

    # Error differences
    error_diff = compare_field(attempts, 'error')
    if error_diff:
        diff_blocks.append(
            render_diff_block(
                template_attempt_diff,
                summary="≠ Error Differences",
                content=error_diff
            )
        )

    # URL differences
    url_diff = compare_field(attempts, "url")
    if url_diff:
        diff_blocks.append(
            render_diff_block(
                template_attempt_diff,
                summary="≠ URL Differences",
                content=url_diff
            )
        )

    # Duration differences（可选，保留但更理性）
    duration_diff = compare_numeric_field(attempts, "duration")
    if duration_diff:
        diff_blocks.append(
            render_diff_block(
                template_attempt_diff,
                summary="≠ Duration Differences",
                content=duration_diff
            )
        )

    # Attachment differences（只告诉“是否变化”，不展开）
    attachment_diff = compare_attachments(attempts)
    if attachment_diff:
        diff_blocks.append(
            render_diff_block(
                template_attempt_diff,
                summary="≠ Attachment Differences",
                content=attachment_diff
            )
        )

    return "".join(diff_blocks)


def render_diff_block(template: str, summary: str, content: str) -> str:
    """统一渲染 diff block，避免 replace 链式调用混乱"""
    return (
        template
        .replace("{{summary}}", summary)
        .replace("{{content}}", content)
    )


def compare_field(attempts: list[dict], field: str) -> str:
    """
    Compare string-like fields (error, url).
    Returns a compact diff summary instead of full values.
    """
    values = [a.get(field) for a in attempts if a.get(field)]
    unique = list(set(values))

    if len(unique) <= 1:
        return ""

    # 不直接 dump 全文本，避免和 Failure Panel 重复
    return f"{len(unique)} distinct values across attempts"


def compare_numeric_field(attempts: list[dict], field: str) -> str:
    """Compare numeric fields like duration"""
    values = [a.get(field) for a in attempts if isinstance(a.get(field), (int, float))]

    if len(values) <= 1:
        return ""

    min_v, max_v = min(values), max(values)

    if min_v == max_v:
        return ""

    return f"Range: {min_v}s → {max_v}s"


def compare_attachments(attempts: list[dict]) -> str:
    """
    Compare attachment existence across attempts.
    Only reports which artifact types are inconsistent.
    """
    diffs = []

    for field, label in [
        ("has_screenshot", "Screenshot"),
        ("has_video", "Video"),
        ("has_trace", "Trace"),
    ]:
        values = {a.get(field) for a in attempts}
        if len(values) > 1:
            diffs.append(label)

    if not diffs:
        return ""

    return "Inconsistent artifacts: " + ", ".join(diffs)
