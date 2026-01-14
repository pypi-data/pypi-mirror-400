from typing import List
from core.linter_integration import LinterRunner, LintViolation
import json

class AngularSupport:
    name = "angular"
    extensions: List[str] = [".ts", ".html", ".scss"]
    layer_markers: List[str] = ["src", "app", "components", "services", "modules", "pipes", "directives"]
    forbidden_terms: List[str] = ["useState", "useEffect", "React."]

    def get_linter_runner(self) -> LinterRunner:
        command = ["npx", "eslint", "{path}", "-f", "json"]

        def parser(output: str) -> List[LintViolation]:
            try:
                data = json.loads(output)
            except Exception:
                return []

            violations: List[LintViolation] = []
            for file_result in data:
                file_path = file_result.get("filePath")
                for msg in file_result.get("messages", []):
                    rule_id = msg.get("ruleId") or "eslint"
                    violations.append(
                        LintViolation(
                            tool="eslint",
                            tool_rule_id=str(rule_id),
                            file=file_path,
                            line=msg.get("line") or 1,
                            column=msg.get("column") or 1,
                            message=msg.get("message") or "",
                        )
                    )
            return violations

        return LinterRunner("eslint", command, parser)
