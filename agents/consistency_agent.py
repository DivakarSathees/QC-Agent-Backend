from agents.base_agent import BaseAgent

class ConsistencyAgent(BaseAgent):
    def analyze(self, description: str):
        prompt = f"""
You are a Consistency Quality Checker Agent.
Find contradictions, unclear parts, or logical mismatches.

Return JSON:
{{
  "inconsistency_score": "<0-100>",
  "inconsistencies": ["..."],
  "remarks": "summary"
}}

Description:
---
{description}
---
"""
        return self.run_prompt(prompt)
