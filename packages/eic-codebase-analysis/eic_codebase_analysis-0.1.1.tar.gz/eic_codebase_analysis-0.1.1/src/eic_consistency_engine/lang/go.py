from typing import List
from pathlib import Path
from core.linter_integration import LinterRunner, LintViolation

class GoSupport:
    name = "go"
    extensions: List[str] = [".go"]
    layer_markers: List[str] = ["cmd", "internal", "pkg"]
    forbidden_terms: List[str] = []

    def get_linter_runner(self) -> LinterRunner:
        # golangci-lint run --out-format json {path}
        # Usually golangci-lint run {path} works if path is a dir.
        command = ["golangci-lint", "run", "--out-format", "json", "{path}"]

        def parser(output: str) -> List[LintViolation]:
            import json
            try:
                data = json.loads(output)
                # Ensure list or extract from dict
                if isinstance(data, dict) and "Issues" in data:
                     data = data["Issues"]
                if not isinstance(data, list):
                     return []
                
                violations = []
                for item in data:
                    pos = item.get("Pos", {})
                    if not isinstance(pos, dict):
                        pos = {}
                        
                    violations.append(LintViolation(
                        tool="golangci-lint",
                        tool_rule_id=item.get("FromLinter", "unknown"),
                        file=pos.get("Filename", "") or "",
                        line=pos.get("Line", 0) or 0,
                        column=pos.get("Column", 0) or 0,
                        message=item.get("Text", "") or ""
                    ))
                return violations
            except Exception:
                return []

        return LinterRunner("golangci-lint", command, parser)
