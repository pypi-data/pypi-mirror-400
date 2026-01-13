"""JSON report generator."""

import json
from datetime import datetime, timezone
from typing import List

from screenshot_guard.detector import Finding


class JSONReporter:
    """Generate JSON reports from findings."""

    def generate(self, findings: List[Finding]) -> str:
        """Generate a JSON report."""
        report = {
            "tool": "screenshot-guard",
            "version": "0.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total": len(findings),
                "critical": len([f for f in findings if f.severity == "critical"]),
                "high": len([f for f in findings if f.severity == "high"]),
                "medium": len([f for f in findings if f.severity == "medium"]),
                "low": len([f for f in findings if f.severity == "low"]),
                "from_ocr": len([f for f in findings if f.from_ocr]),
            },
            "findings": [
                {
                    "file": str(finding.file_path),
                    "line": finding.line_number,
                    "column": finding.column,
                    "type": finding.pattern_name,
                    "severity": finding.severity,
                    "provider": finding.provider,
                    "description": finding.description,
                    "match": finding.redacted_match(),
                    "context": finding.context,
                    "from_ocr": finding.from_ocr,
                }
                for finding in findings
            ],
        }

        return json.dumps(report, indent=2, ensure_ascii=False)
