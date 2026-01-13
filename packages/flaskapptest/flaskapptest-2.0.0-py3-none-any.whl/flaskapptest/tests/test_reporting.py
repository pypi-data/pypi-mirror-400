from flaskapptest.core.reporting import ReportGenerator


def test_report_summary():
    report = ReportGenerator()
    summary = report.summary([
        {"passed": True},
        {"passed": False},
    ])

    assert summary["total"] == 2
    assert summary["passed"] == 1
