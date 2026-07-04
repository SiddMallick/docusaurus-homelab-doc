#!/usr/bin/env python3

import json
from pathlib import Path
from collections import Counter
from datetime import datetime

REPORT_DIR = Path("reports")


class SecurityReport:

    def __init__(self):
        self.summary = Counter()
        self.sections = []

    ############################################################
    # Helpers
    ############################################################

    def _find(self, filename):
        return list(REPORT_DIR.rglob(filename))

    ############################################################
    # npm audit
    ############################################################

    def parse_npm_audit(self):

        files = self._find("npm-audit.json")

        if not files:
            self.sections.append(("NPM Audit", "No report found"))
            return

        file = files[0]

        with open(file) as f:
            data = json.load(f)

        vulns = data.get("metadata", {}).get("vulnerabilities", {})

        self.summary["critical"] += vulns.get("critical", 0)
        self.summary["high"] += vulns.get("high", 0)
        self.summary["moderate"] += vulns.get("moderate", 0)
        self.summary["low"] += vulns.get("low", 0)

        self.sections.append(
            (
                "NPM Audit",
                f"""
Critical : {vulns.get('critical',0)}
High     : {vulns.get('high',0)}
Moderate : {vulns.get('moderate',0)}
Low      : {vulns.get('low',0)}
""",
            )
        )

    ############################################################
    # Semgrep SARIF
    ############################################################

    def parse_semgrep(self):

        files = self._find("semgrep.sarif")

        if not files:
            self.sections.append(("Semgrep", "No report found"))
            return

        file = files[0]

        with open(file) as f:
            sarif = json.load(f)

        results = sarif["runs"][0].get("results", [])

        counts = Counter()

        for r in results:

            level = r.get("level", "warning").lower()

            if level == "error":
                counts["high"] += 1
            elif level == "warning":
                counts["medium"] += 1
            else:
                counts["low"] += 1

        self.summary.update(counts)

        self.sections.append(
            (
                "Semgrep",
                f"""
Findings : {len(results)}

High     : {counts['high']}
Medium   : {counts['medium']}
Low      : {counts['low']}
""",
            )
        )

    ############################################################
    # Trivy
    ############################################################

    def parse_trivy(self):

        files = self._find("trivy-scan-results.json")

        if not files:
            self.sections.append(("Trivy", "No report found"))
            return

        file = files[0]

        with open(file) as f:
            data = json.load(f)

        counts = Counter()

        for result in data.get("Results", []):

            for vuln in result.get("Vulnerabilities", []):

                sev = vuln.get("Severity", "").lower()

                counts[sev] += 1

        self.summary.update(counts)

        self.sections.append(
            (
                "Trivy",
                f"""
Critical : {counts['critical']}
High     : {counts['high']}
Medium   : {counts['medium']}
Low      : {counts['low']}
Unknown  : {counts['unknown']}
""",
            )
        )

    ############################################################
    # Markdown
    ############################################################

    def generate_markdown(self):

        lines = []

        lines.append("# Security Scan Report\n")

        lines.append(
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
        )

        lines.append("## Overall Summary\n")

        lines.append("| Severity | Count |")
        lines.append("|----------|------:|")

        for sev in [
            "critical",
            "high",
            "medium",
            "moderate",
            "low",
            "unknown",
        ]:
            lines.append(f"| {sev.title()} | {self.summary.get(sev,0)} |")

        lines.append("")

        total = sum(self.summary.values())

        if self.summary.get("critical", 0):
            status = "❌ FAILED"
        elif self.summary.get("high", 0):
            status = "⚠️ HIGH RISK"
        elif total:
            status = "🟡 Findings Present"
        else:
            status = "✅ CLEAN"

        lines.append(f"## Overall Status\n\n**{status}**\n")

        for title, body in self.sections:

            lines.append(f"## {title}\n")
            lines.append("```")
            lines.append(body.strip())
            lines.append("```")
            lines.append("")

        with open("security-report.md", "w") as f:
            f.write("\n".join(lines))

        print("Generated security-report.md")


def main():

    report = SecurityReport()

    report.parse_npm_audit()
    report.parse_semgrep()
    report.parse_trivy()

    report.generate_markdown()


if __name__ == "__main__":
    main()