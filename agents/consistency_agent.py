# from agents.base_agent import BaseAgent

# class ConsistencyAgent(BaseAgent):
#     def analyze(self, description: str, results: dict = None):
#         """
#         Analyze consistency in the project description,
#         optionally using prior agent results for deeper reasoning.
#         """
#         print(f"[ConsistencyAgent] Analyzing consistency with prior results.")
#         print(results)
#         prompt = f"""
# You are a Consistency Quality Checker Agent.
# Your job is to find contradictions, unclear parts, or logical mismatches.

# You may use insights from prior agent results if provided:
# {results}

# Return JSON:
# {{
#   "inconsistency_score": "<0-100>",
#   "inconsistencies": ["..."],
#   "remarks": "summary"
# }}

# Description:
# ---
# {description}
# ---
# """
#         return self.run_prompt(prompt)


from agents.base_agent import BaseAgent

class ConsistencyAgent(BaseAgent):
    def analyze(self, description: str, results: dict = None):
        """
        Analyze consistency in the project description,
        using prior agent results (like completeness and test coverage)
        for deeper contextual reasoning.
        """

        print(f"[ConsistencyAgent] 🔍 Analyzing consistency with prior results.")
        print(results)

        # Extract relevant context safely
        completeness_info = results.get("completeness", {})
        test_coverage_info = results.get("test_coverage", {})

        missing_components = completeness_info.get("missing_components", [])
        missing_details = test_coverage_info.get("missing_details", [])

        # Build a compact, structured context summary
        context_summary = {
            "completeness_score": completeness_info.get("completeness_score"),
            "missing_components": missing_components,
            "coverage_score": test_coverage_info.get("coverage_score"),
            "missing_test_details": missing_details,
            "previous_remarks": {
                k: v.get("remarks") for k, v in (results or {}).items() 
                if k not in ["completeness", "test_coverage"]
            },
        }

        print(f"[ConsistencyAgent] Context Summary for Prompt:")
        print(context_summary)

        prompt = f"""
You are a **Consistency Quality Checker Agent**.
Your role is to identify contradictions, unclear logic, or mismatched expectations
in the given project description — especially comparing expected behaviors
(in description) vs actual coverage (from tests).

You have access to prior agent insights summarized below:
{context_summary}

Focus especially on:
- Conflicts between description and missing components or missing test coverage.
- Logical or structural contradictions.
- Inconsistent error codes, data flows, or wording.

Return JSON:
{{
  "inconsistency_score": "<0-100>",
  "inconsistencies": ["List of specific mismatches or contradictions."],
  "remarks": "Concise summary of consistency findings."
}}

Description:
---
{description}
---
"""
        return self.run_prompt(prompt)
