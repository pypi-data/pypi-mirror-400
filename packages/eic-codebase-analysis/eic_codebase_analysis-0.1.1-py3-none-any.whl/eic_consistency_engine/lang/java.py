from typing import List
from core.linter_integration import LinterRunner, LintViolation
import re

class JavaSupport:
    name = "java"
    extensions: List[str] = [".java", ".jar", ".xml"]
    layer_markers: List[str] = ["src", "main", "test", "java", "resources", "webapp", "domain", "repository", "service", "controller"]
    forbidden_terms: List[str] = ["Console.WriteLine", "def "]

    def get_linter_runner(self) -> LinterRunner:
        # Assumes Maven project. Adjust for Gradle or pure javac if needed.
        # Wrapped in cmd /c to avoid WinError 2 if mvn is not in PATH
        command = ["cmd", "/c", "mvn", "compile", "-q", "-f", "{path}/pom.xml"]

        def parser(output: str) -> List[LintViolation]:
            # Maven/Javac output:
            # [WARNING] /path/to/File.java:[10,20] warning: [cast] redundant cast
            violations = []
            regex = re.compile(r"^\[WARNING\]\s+(.*):\[(\d+),(\d+)\]\s+warning:\s+(?:\[(.*)\])?\s*(.*)$")
            
            for line in output.splitlines():
                line = line.strip()
                m = regex.match(line)
                if m:
                    file_path, line_num, col, category, msg = m.groups()
                    violations.append(LintViolation(
                        tool="mvn-javac",
                        tool_rule_id=category or "javac",
                        file=file_path,
                        line=int(line_num),
                        column=int(col),
                        message=msg
                    ))
            return violations

        return LinterRunner("mvn-javac", command, parser)
