"""SARIF report generator for GitHub Security integration."""

import json
from datetime import datetime, timezone
from typing import List

from screenshot_guard.detector import Finding


class SARIFReporter:
    """Generate SARIF reports compatible with GitHub Security tab."""

    SARIF_VERSION = "2.1.0"
    SCHEMA_URI = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"

    def generate(self, findings: List[Finding]) -> str:
        """Generate a SARIF report.

        Args:
            findings: List of findings to report

        Returns:
            SARIF JSON string
        """
        # Collect unique rules
        rules = {}
        for finding in findings:
            rule_id = self._make_rule_id(finding.pattern_name)
            if rule_id not in rules:
                rules[rule_id] = {
                    "id": rule_id,
                    "name": finding.pattern_name,
                    "shortDescription": {"text": finding.pattern_name},
                    "fullDescription": {"text": finding.description or finding.pattern_name},
                    "defaultConfiguration": {
                        "level": self._severity_to_level(finding.severity)
                    },
                    "properties": {
                        "tags": ["security", "secrets", finding.provider],
                        "precision": "high",
                    },
                }

        # Build results
        results = []
        for finding in findings:
            result = {
                "ruleId": self._make_rule_id(finding.pattern_name),
                "level": self._severity_to_level(finding.severity),
                "message": {
                    "text": f"Potential {finding.pattern_name} detected"
                    + (" (via OCR)" if finding.from_ocr else "")
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": str(finding.file_path).replace("\\", "/"),
                            },
                            "region": {
                                "startLine": finding.line_number,
                                "startColumn": finding.column,
                            },
                        }
                    }
                ],
                "partialFingerprints": {
                    "primaryLocationLineHash": f"{finding.file_path}:{finding.line_number}:{finding.pattern_name}"
                },
            }
            results.append(result)

        # Build SARIF document
        sarif = {
            "$schema": self.SCHEMA_URI,
            "version": self.SARIF_VERSION,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Screenshot Guard",
                            "version": "0.1.0",
                            "informationUri": "https://github.com/Keyvanhardani/screenshot-guard",
                            "rules": list(rules.values()),
                        }
                    },
                    "results": results,
                    "invocations": [
                        {
                            "executionSuccessful": True,
                            "endTimeUtc": datetime.now(timezone.utc).isoformat(),
                        }
                    ],
                }
            ],
        }

        return json.dumps(sarif, indent=2)

    def _make_rule_id(self, name: str) -> str:
        """Convert pattern name to rule ID."""
        return name.lower().replace(" ", "-").replace("_", "-")

    def _severity_to_level(self, severity: str) -> str:
        """Convert severity to SARIF level."""
        mapping = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
        }
        return mapping.get(severity, "warning")
