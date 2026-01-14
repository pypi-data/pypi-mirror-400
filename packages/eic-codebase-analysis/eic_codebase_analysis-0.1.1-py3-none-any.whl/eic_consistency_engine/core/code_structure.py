import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class StructureExtractor:
    def __init__(self, root_path: Path):
        self.root_path = root_path

    def extract(self, language_hints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts structural metrics from the repository using language-specific hints.
        """
        file_types = {}
        total_size = 0
        total_files = 0
        depths = []
        dir_patterns = set()
        
        relevant_extensions = language_hints.get("extensions", [])
        layer_markers = language_hints.get("layer_markers", [])

        for root, dirs, files in os.walk(self.root_path):
            rel_path = Path(root).relative_to(self.root_path)
            depth = len(rel_path.parts)
            
            # Check for layer markers in directory names
            for marker in layer_markers:
                if marker in rel_path.parts:
                    dir_patterns.add(marker)
            
            for file in files:
                ext = Path(file).suffix
                if relevant_extensions and ext not in relevant_extensions:
                    continue

                file_types[ext] = file_types.get(ext, 0) + 1
                total_files += 1
                depths.append(depth)
                
                # File size
                try:
                    size = (Path(root) / file).stat().st_size
                    total_size += size
                except OSError:
                    pass

        return {
            "file_types": file_types,
            "total_size": total_size,
            "depths": depths,
            "dir_patterns": list(dir_patterns),
            "total_files": total_files
        }
