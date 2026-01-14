import json
import importlib
import os
from pathlib import Path
from typing import List, Dict, Any
from core.code_structure import StructureExtractor
from core.gemini_client import GeminiClient

def run(language: str, repo: Path, name: str, with_ai: bool):
    print(f"Analyzing {name} ({repo}) as {language}...")
    
    # Load support
    try:
        module = importlib.import_module(f"lang.{language}")
        support_class = getattr(module, f"{language.capitalize()}Support")
        support = support_class()
    except Exception as e:
        print(f"Error loading language support: {e}")
        return

    # Load Baseline and Standards
    baseline_path = Path(f"consistency-engine/data/baselines/{language}/baseline.json")
    standards_path = Path(f"consistency-engine/data/standards/{language}/linter_spec.json")
    
    if not baseline_path.exists():
        print("Baseline not found. Run init first.")
        return
        
    with open(baseline_path, 'r') as f:
        baseline = json.load(f)
        
    standard_rules_map = {}
    standard_rules_list = []
    if standards_path.exists():
        with open(standards_path, 'r') as f:
            standards = json.load(f)
            # Mapping: list of objects with tool_rule_ids (list or str) and standard_id
            for mapping in standards.get("rule_mappings", []):
                std_id = mapping.get("standard_id")
                # Handle possible keys for tool rules
                tool_ids = mapping.get("tool_rule_ids") or mapping.get("tool_rules") or []
                if isinstance(tool_ids, str): tool_ids = [tool_ids]
                for tid in tool_ids:
                     standard_rules_map[tid] = std_id
            standard_rules_list = standards.get("standard_rules", [])

    # Analyze New Repo
    linter = support.get_linter_runner()
    extractor = StructureExtractor(repo)
    hints = {"extensions": support.extensions, "layer_markers": support.layer_markers}
    structure_metrics = extractor.extract(hints)
    
    violations = linter.run(repo)
    
    # Process Violations
    rule_counts = {}
    standard_violations = {} # standard_id -> count
    total_violations = len(violations)
    
    for v in violations:
        rule_counts[v.tool_rule_id] = rule_counts.get(v.tool_rule_id, 0) + 1
        std_id = standard_rules_map.get(v.tool_rule_id)
        if std_id:
            standard_violations[std_id] = standard_violations.get(std_id, 0) + 1
            
    # Count Lines
    total_lines = 0
    for root, _, files in os.walk(repo):
        for file in files:
            if Path(file).suffix in support.extensions:
                try:
                    with open(Path(root) / file, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += sum(1 for _ in f)
                except:
                    pass

    # Normalized Metrics
    new_metrics = {
        "lint_metrics": {
            "total_lines": total_lines,
            "total_violations": total_violations,
            "violations_per_1000_lines": (total_violations / total_lines * 1000) if total_lines else 0,
            "rules": {
                rid: {
                    "count": count,
                    "per_1000_lines": (count / total_lines * 1000) if total_lines else 0
                } for rid, count in rule_counts.items()
            },
            "standard_violations": standard_violations
        },
        "structure_metrics": structure_metrics
    }
    
    # Save Report
    report_dir = Path(f"consistency-engine/reports/{name}")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    with open(report_dir / "scan_summary.json", "w") as f:
        json.dump(new_metrics, f, indent=2)
        
    print(f"Report saved to {report_dir}")
    
    if with_ai:
        try:
            gemini = GeminiClient()
            # Select snippets
            snippets = ""
            sorted_files = []
            for root, _, files in os.walk(repo):
                for file in files:
                    if Path(file).suffix in support.extensions:
                        path = Path(root) / file
                        try:
                            size = path.stat().st_size
                            sorted_files.append((path, size))
                        except: pass
            sorted_files.sort(key=lambda x: x[1], reverse=True)
            
            for path, size in sorted_files[:3]:
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if len(content) > 5000: content = content[:5000] + "\n...[TRUNCATED]"
                        snippets += f"--- File: {path.name} ---\n{content}\n\n"
                except:
                    pass
            
            print("Running AI analysis...")
            ai_results = gemini.analyze_repo(language, baseline, new_metrics, standard_rules_list, snippets)
            
            with open(report_dir / "consistency_scores.json", "w") as f:
                json.dump(ai_results, f, indent=2)
            
            if "summary" in ai_results:
                 with open(report_dir / "ai_summary.md", "w") as f:
                     f.write(ai_results["summary"])
            
            if "recommendations" in ai_results:
                 with open(report_dir / "ai_recommendations.md", "w") as f:
                     # assuming list
                     f.write("# Recommendations\n\n")
                     for rec in ai_results["recommendations"]:
                         f.write(f"- {rec}\n")
            
            print("AI analysis complete.")
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
