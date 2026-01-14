from typing import List, Any
from core.language_models import LanguageSupport
from core.linter_integration import LinterRunner, generic_json_parser

class PythonSupport:
    name = "python"
    extensions = [".py"]
    layer_markers = ["src", "tests", "test", "api", "domain", "infrastructure", "scripts", "utils", "models", "services"]
    forbidden_terms = [".ps1", "Write-Host", "func main()", "public static void", "using namespace", "Get-ChildItem"]

    def get_linter_runner(self) -> LinterRunner:
        # Wrapped in cmd /c for Windows compatibility
        return LinterRunner(
            tool_name="ruff",
            command_template=["cmd", "/c", "ruff", "check", "{path}", "--output-format", "json"],
            parser_func=self._parse_ruff
        )

    def _parse_ruff(self, output: str) -> List[Any]:
        # Ruff JSON output is a list of objects
        field_map = {
            "rule_id": "code",
            "file": "filename",
            "line": "line",
            "column": "column",
            "message": "message"
        }
        return generic_json_parser(output, field_map, "ruff")
