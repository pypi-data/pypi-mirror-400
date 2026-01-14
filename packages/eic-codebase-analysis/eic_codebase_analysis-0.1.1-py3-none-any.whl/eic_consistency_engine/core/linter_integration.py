import subprocess
import json
from typing import List, Dict, Any, Callable
from pydantic import BaseModel
from pathlib import Path

class LintViolation(BaseModel):
    tool: str
    tool_rule_id: str
    file: str
    line: int
    column: int
    message: str

class LinterRunner:
    def __init__(self, tool_name: str, command_template: List[str], parser_func: Callable[[str], List[LintViolation]]):
        self.tool_name = tool_name
        self.command_template = command_template
        self.parser_func = parser_func

    def run(self, repo_path: Path) -> List[LintViolation]:
        # Construct command: replace {path} with repo_path
        cmd = [str(part).replace("{path}", str(repo_path)) for part in self.command_template]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            # Some linters exit with non-zero on violations, so we don't strictly check=True
            # But if stderr has errors that are not violations, we might want to log them.
            
            output = result.stdout
            if not output and result.stderr:
                 # Fallback if linter writes to stderr (rare for json output but possible)
                 output = result.stderr
            
            return self.parser_func(output)
        except Exception as e:
            print(f"Error running linter {self.tool_name}: {e}")
            return []

def generic_json_parser(output: str, field_map: Dict[str, str], tool_name: str) -> List[LintViolation]:
    """
    Parses a generic JSON output where field_map maps standard fields to JSON keys.
    """
    try:
        data = json.loads(output)
        if isinstance(data, dict): # Sometimes wrapped in a key
            # heuristics to find the list? Or require strict path?
            # keeping it simple for now, assuming list of objects
            pass
        
        if not isinstance(data, list):
            # Try to find a list in values
            found = False
            for v in data.values():
                if isinstance(v, list):
                    data = v
                    found = True
                    break
            if not found:
                return []

        violations = []
        for item in data:
            violations.append(LintViolation(
                tool=tool_name,
                tool_rule_id=item.get(field_map.get("rule_id", "code"), "unknown"),
                file=item.get(field_map.get("file", "filename"), ""),
                line=item.get(field_map.get("line", "line"), 0) or 0,
                column=item.get(field_map.get("column", "column"), 0) or 0,
                message=item.get(field_map.get("message", "message"), "")
            ))
        return violations
    except json.JSONDecodeError:
        return []
