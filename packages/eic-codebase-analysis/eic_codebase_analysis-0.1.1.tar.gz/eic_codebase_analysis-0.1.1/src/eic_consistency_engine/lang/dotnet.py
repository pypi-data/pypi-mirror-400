from typing import List
from core.linter_integration import LinterRunner, LintViolation
import re

class DotnetSupport:
    name = "dotnet"
    extensions: List[str] = [".cs", ".csproj", ".sln"]
    layer_markers: List[str] = ["Controllers", "Services", "Models", "Data", "DTOs", "Infrastructure"]
    forbidden_terms: List[str] = ["system.out.println", "def "]

    def get_linter_runner(self) -> LinterRunner:
        # Uses dotnet build to capture warnings/errors
        command = ["dotnet", "build", "{path}", "-nologo", "-clp:NoSummary"]

        def parser(output: str) -> List[LintViolation]:
            # MSBuild output format:
            # File(Line,Col): error/warning Code: Message
            # Example: C:\Path\File.cs(10,20): warning CS0168: The variable 'e' is declared but never used
            violations = []
            regex = re.compile(r"^(.*)\((\d+),(\d+)\):\s+(error|warning)\s+(\w+):\s+(.*)$")
            
            for line in output.splitlines():
                line = line.strip()
                m = regex.match(line)
                if m:
                    file_path, line_num, col, severity, code, msg = m.groups()
                    violations.append(LintViolation(
                        tool="dotnet-build",
                        tool_rule_id=code,
                        file=file_path,
                        line=int(line_num),
                        column=int(col),
                        message=msg
                    ))
            return violations

        return LinterRunner("dotnet-build", command, parser)
