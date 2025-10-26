from agents.base_agent import BaseAgent
import json

class CorrectionAgent(BaseAgent):
    def correct(self, description: str, qc_results: dict):
        prompt = f"""
You are a Project Description Correction Agent.

Your task:
- Fix and complete the project description using the QC feedback.
- Preserve the original **format, HTML tags, numbering, tone, and structure**.
- Fill in missing or incomplete parts **without hallucinating new features**.
- Ensure the final corrected description is clear, consistent, and complete.

Input Description:
---
{description}
---

QC Feedback:
{json.dumps(qc_results, indent=2)}

Return JSON:
{{
  "corrected_description": "<the improved project description text>",
  "corrections_made": ["..."],
  "remarks": "summary of changes"
}}
"""
        return self.run_prompt(prompt)
