from agents.base_agent import BaseAgent
import json

class ImplementationReadinessAgent(BaseAgent):
    def analyze(self, results: dict):
        prompt = f"""
You are an Implementation Readiness Agent.
Given the QC results below, determine if this project is ready for implementation.

QC Results:
{json.dumps(results, indent=2)}

Return JSON:
{{
  "is_ready_for_implementation": true/false,
  "justification": "reasoning",
  "overall_score": "<0-100>"
}}
"""
        return self.run_prompt(prompt)
