from typing import List, Dict, Any, Protocol
from .linter_integration import LinterRunner

class LanguageSupport(Protocol):
    name: str
    extensions: List[str]
    layer_markers: List[str]
    forbidden_terms: List[str] = [] # Terms that should not appear in the guide
    
    def get_linter_runner(self) -> LinterRunner:
        ...
