import json
import importlib
import os
from pathlib import Path
from typing import List, Dict
from core.code_structure import StructureExtractor
from core.linter_integration import LintViolation
from core.gemini_client import GeminiClient

def run(language: str, refs: List[Path]):
    print(f"Loading support for {language}...")
    try:
        module = importlib.import_module(f"lang.{language}")
        support_class = getattr(module, f"{language.capitalize()}Support")
        support = support_class()
    except (ImportError, AttributeError) as e:
        print(f"Error loading language support: {e}")
        return

    print("Analyzing reference repositories...")
    
    # Aggregated metrics
    agg_structure = {
        "file_types": {},
        "total_size": 0,
        "depths": [],
        "dir_patterns": set(),
        "total_files": 0
    }
    
    rule_counts = {}
    sample_messages = {}
    total_violations = 0
    total_lines = 0 # Approximate
    
    linter = support.get_linter_runner()
    
    for ref in refs:
        ref_path = Path(ref)
        if not ref_path.exists():
            print(f"Skipping invalid path: {ref}")
            continue
            
        print(f"Processing {ref}...")
        
        # Structure
        extractor = StructureExtractor(ref_path)
        hints = {"extensions": support.extensions, "layer_markers": support.layer_markers}
        metrics = extractor.extract(hints)
        
        # Merge structure
        for ext, count in metrics["file_types"].items():
            agg_structure["file_types"][ext] = agg_structure["file_types"].get(ext, 0) + count
        agg_structure["total_size"] += metrics["total_size"]
        agg_structure["depths"].extend(metrics["depths"])
        agg_structure["dir_patterns"].update(metrics["dir_patterns"])
        agg_structure["total_files"] += metrics["total_files"]
        
        # Lint
        violations = linter.run(ref_path)
        total_violations += len(violations)
        
        for v in violations:
            rule_counts[v.tool_rule_id] = rule_counts.get(v.tool_rule_id, 0) + 1
            if v.tool_rule_id not in sample_messages:
                sample_messages[v.tool_rule_id] = []
            if len(sample_messages[v.tool_rule_id]) < 3:
                 sample_messages[v.tool_rule_id].append(v.message)
            
        # Count lines (simple walk for relevant extensions)
        for root, _, files in os.walk(ref_path):
            for file in files:
                if Path(file).suffix in support.extensions:
                    try:
                        with open(Path(root) / file, 'r', encoding='utf-8', errors='ignore') as f:
                            total_lines += sum(1 for _ in f)
                    except:
                        pass

    # Compute Final Baseline
    avg_file_size = agg_structure["total_size"] / agg_structure["total_files"] if agg_structure["total_files"] else 0
    avg_depth = sum(agg_structure["depths"]) / len(agg_structure["depths"]) if agg_structure["depths"] else 0
    
    baseline = {
        "language": language,
        "lint_metrics": {
            "total_lines": total_lines,
            "total_violations": total_violations,
            "violations_per_1000_lines": (total_violations / total_lines * 1000) if total_lines else 0,
            "rules": {
                rid: {
                    "count": count,
                    "per_1000_lines": (count / total_lines * 1000) if total_lines else 0
                } for rid, count in rule_counts.items()
            }
        },
        "structure_metrics": {
            "file_types": agg_structure["file_types"],
            "avg_file_size": avg_file_size,
            "avg_depth": avg_depth,
            "dir_patterns": list(agg_structure["dir_patterns"])
        }
    }
    
    # Save
    out_dir = Path("consistency-engine/data/baselines") / language
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "baseline.json"
    
    with open(out_file, "w") as f:
        json.dump(baseline, f, indent=2)
        
    print(f"Baseline saved to {out_file}")

    # Step 2: AI Generation
    try:
        gemini = GeminiClient()
        print("Generating standards using AI...")
        standards_data = gemini.generate_standards(language, baseline["lint_metrics"], sample_messages)
        
        if standards_data:
            standards_dir = Path("consistency-engine/data/standards") / language
            standards_dir.mkdir(parents=True, exist_ok=True)
            
            # Save linter spec
            with open(standards_dir / "linter_spec.json", "w") as f:
                json.dump(standards_data, f, indent=2)
            print(f"Linter spec saved to {standards_dir / 'linter_spec.json'}")
            
            # Generate Guide
            print("Generating implementation guide...")
            guide = gemini.generate_guide(language, baseline["structure_metrics"], standards_data.get("standard_rules", []))
            
            if guide:
                # Validation
                forbidden = getattr(support, 'forbidden_terms', [])
                if any(term in guide for term in forbidden):
                     print(f"Guide validation failed. Contains forbidden terms: {[t for t in forbidden if t in guide]}")
                else:
                    with open(standards_dir / "implementation_guide.md", "w", encoding='utf-8') as f:
                        f.write(guide)
                    print(f"Implementation guide saved to {standards_dir / 'implementation_guide.md'}")
    except ValueError:
        print("Skipping AI steps (GEMINI_API_KEY not found)")
    except Exception as e:
        print(f"Error during AI generation: {e}")
