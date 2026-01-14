from typing import List
from core.linter_integration import LinterRunner, LintViolation
import json

class ReactSupport:
    name = "react"
    extensions: List[str] = [".jsx", ".tsx", ".js", ".ts"]
    layer_markers: List[str] = ["src", "components", "hooks", "context", "utils", "pages"]
    forbidden_terms: List[str] = ["ng-", "@angular"]

    def get_linter_runner(self) -> LinterRunner:
        command = ["cmd", "/c", "npx", "eslint", "{path}", "-f", "json"]

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
