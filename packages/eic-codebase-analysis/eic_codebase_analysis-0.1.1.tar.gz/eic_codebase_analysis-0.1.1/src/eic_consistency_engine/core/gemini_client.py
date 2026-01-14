import os
import google.generativeai as genai
import json
from typing import Dict, Any, Optional, List

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            # We allow initialization without key, but methods will fail or need check
            pass
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_standards(self, language: str, lint_metrics: Dict, sample_messages: Dict) -> Dict:
        if not hasattr(self, 'model'):
             raise ValueError("GEMINI_API_KEY not configured")

        prompt = f"""
You are a senior {language} developer and static analysis expert.

We have lint rule statistics for {language}, including rule IDs and their frequencies in our reference repositories.
Your tasks:

1. Group tool-specific rule IDs into high-level COMPANY STANDARD RULES.
2. For each standard rule, define:
   - id (e.g., "{language}.unused_public_function")
   - category (style, naming, complexity, security, testing, architecture)
   - severity (low/medium/high)
   - short description
   - rationale

3. Produce a mapping from standard rules to tool rule IDs.

Input (JSON):
Lint Metrics Rules: {json.dumps(lint_metrics.get('rules', {}), indent=2)}
Sample Messages: {json.dumps(sample_messages, indent=2)}

Output (JSON only):
{{
  "standard_rules": [...],
  "rule_mappings": [...]
}}
"""
        try:
            response = self.model.generate_content(prompt)
            return self._extract_json(response.text)
        except Exception as e:
            print(f"Error generating standards: {e}")
            return {}

    def generate_guide(self, language: str, structure_metrics: Dict, standard_rules: List[Dict]) -> str:
        if not hasattr(self, 'model'):
             raise ValueError("GEMINI_API_KEY not configured")

        prompt = f"""
You are an experienced {language} architect.

We have extracted structural metrics from our reference {language} repositories:

STRUCTURE_METRICS (JSON):
{json.dumps(structure_metrics, indent=2)}

We also have corporate standard rules for {language}:

STANDARD_RULES (JSON):
{json.dumps(standard_rules, indent=2)}

Using ONLY the {language}-specific information above:

- Describe the typical project layout (folders, modules, tests, scripts) for {language}.
- Describe naming conventions (files, modules, functions/classes, tests).
- Describe decomposition practices (how responsibilities are split across files/modules).
- Describe typical component sizes (rough guidelines, e.g., functions under X lines, modules under Y lines), based on averages and distributions, not exact limits.
- Do NOT invent patterns from other languages or frameworks. Stay within idiomatic {language} practices.

Output:
Return a Markdown document with sections:

# {language} Implementation Guide

## Overall Architecture
...

## Directory and Module Structure
...

## Naming Conventions
...

## Decomposition and Component Size
...

## Testing and Quality Practices
...

Only output Markdown.
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating guide: {e}")
            return ""

    def analyze_repo(self, language: str, baseline: Dict, new_metrics: Dict, standards: List[Dict], snippets: str) -> Dict:
         if not hasattr(self, 'model'):
             raise ValueError("GEMINI_API_KEY not configured")

         prompt = f"""
You are a senior {language} architect.

We have:

1) BASELINE_METRICS (JSON) for {language} reference repos:
   {json.dumps(baseline, indent=2)}

2) NEW_REPO_METRICS (JSON):
   {json.dumps(new_metrics, indent=2)}

3) STANDARD_RULES (JSON):
   {json.dumps(standards, indent=2)}

4) Code snippets from the NEW repository:
{snippets}

Task:
- Evaluate how consistent the NEW repository is with baseline {language} practices and our standards.
- Rate four dimensions from 0 to 1:
- structure
- naming
- decomposition
- component_size
- Provide a brief explanation per dimension.
- Provide an overall score 0..1.
- Suggest actionable recommendations (bulleted list).

Output JSON only:
{{
"overall_score": ...,
"dimension_scores": {{...}},
"dimension_explanations": {{...}},
"summary": "...",
"recommendations": [...]
}}
"""
         try:
            response = self.model.generate_content(prompt)
            return self._extract_json(response.text)
         except Exception as e:
            print(f"Error analyzing repo: {e}")
            return {}

    def _extract_json(self, text: str) -> Any:
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return json.loads(text)
        except json.JSONDecodeError:
            return {}
