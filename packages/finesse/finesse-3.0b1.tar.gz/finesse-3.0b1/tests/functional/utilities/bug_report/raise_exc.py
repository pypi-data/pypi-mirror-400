from finesse.utilities.bug_report import bug_report

if __name__ == "__main__":
    try:
        1 / 0
    except Exception:
        bug_report(file="bug_report.md", include_source=True)
