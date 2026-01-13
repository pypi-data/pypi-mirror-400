import pytest

from pytest_attempt_summary.attempt_summary import attach_attempt_summary


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when != "teardown":
        return

    attempts = getattr(item, "_attempts", [])
    if not attempts:
        return

    # rerun 次数（pytest-rerunfailures）
    max_attempts = getattr(item.session.config.option, "reruns", 0)+1
    current_attempt = len(attempts)

    # 只在最后一次执行 attach
    if current_attempt != max_attempts:
        return

    attach_attempt_summary(attempts)