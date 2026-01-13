def build_retry_insight(attempts: list[dict]) -> list[str]:
    if not attempts:
        return ""

    """生成RetryInsight文本"""
    lines = []

    failed = [a for a in attempts if a.get('status') == "FAILED"]
    passed = [a for a in attempts if a.get('status') == "PASSED"]

    # 1️⃣ Flaky 判断
    if failed and passed:
        lines.append("• Test recovered after retry (passed on retry)")
        lines.append("• Likely flaky test (unstable behavior)")
        return lines

    # 2️⃣ Error 是否变化
    errors = {
        a.get('error') for a in attempts
        if isinstance(a, dict) and a.get('error')
    }
    if len(errors) > 1:
        lines.append("• Flaky behavior detected (error changed between attempts)")

    # 3️⃣ URL 是否变化
    urls = {
        a.get('url') for a in attempts
        if isinstance(a, dict) and a.get('url')
    }
    if len(urls) > 1:
        lines.append("• Failure occurred at different URLs")
    return lines
