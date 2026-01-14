from typing import List, Any
from core.language_models import LanguageSupport
from core.linter_integration import LinterRunner, generic_json_parser

class PowershellSupport:
    name = "powershell"
    extensions = [".ps1", ".psm1", ".psd1"]
    layer_markers = ["Public", "Private", "Tests", "Scripts", "functions", "modules"]
    forbidden_terms = ["def ", "import ", "package.json", ".py"]

    def get_linter_runner(self) -> LinterRunner:
        # PSScriptAnalyzer output parser needed
        # Using powershell instead of pwsh for broader compatibility on Windows
        return LinterRunner(
            tool_name="PSScriptAnalyzer",
            command_template=["cmd", "/c", "powershell", "-Command", "Invoke-ScriptAnalyzer -Path '{path}' -Recurse | ConvertTo-Json"],
            parser_func=self._parse_pssa
        )

    def _parse_pssa(self, output: str) -> List[Any]:
        # PSScriptAnalyzer JSON output
        field_map = {
            "rule_id": "RuleName",
            "file": "ScriptName",
            "line": "Line",
            "column": "Column",
            "message": "Message"
        }
        return generic_json_parser(output, field_map, "PSScriptAnalyzer")
