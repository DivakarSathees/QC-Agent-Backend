from agents.base_agent import BaseAgent

class ClarityAgent(BaseAgent):
    def analyze(self, description: str):
        prompt = f"""
You are a Clarity Evaluation Agent.
Check readability, structure, and developer understanding.

Return JSON:
{{
  "clarity_score": "<0-100>",
  "issues": ["..."],
  "suggestions": ["..."]
}}

Description:
---
{description}
---
"""
        return self.run_prompt(prompt)
