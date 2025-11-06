# from agents.base_agent import BaseAgent
# import os
# import zipfile
# import tempfile
# import shutil

# class TestCoverageAgent(BaseAgent):
#     def analyze(self, description: str, tmp_path: str):
#         """
#         Analyze whether the project description provides enough details
#         to implement and pass all test cases found under tmp_path.
#         Automatically extracts .zip files before scanning.
#         """
#         print(f"[TestCoverageAgent] Scanning boilerplate at {tmp_path} for test cases.")
#         test_details = []

#         # --- Step 1: Detect and extract zip ---
#         extracted_dir = None
#         if tmp_path.endswith(".zip") or (
#             os.path.isdir(tmp_path)
#             and any(f.endswith(".zip") for f in os.listdir(tmp_path))
#         ):
#             zip_file_path = tmp_path
#             # If tmp_path is a directory containing the zip, locate it
#             if os.path.isdir(tmp_path):
#                 for f in os.listdir(tmp_path):
#                     if f.endswith(".zip"):
#                         zip_file_path = os.path.join(tmp_path, f)
#                         break

#             extracted_dir = tempfile.mkdtemp()
#             print(f"[TestCoverageAgent] Extracting zip {zip_file_path} → {extracted_dir}")
#             with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
#                 zip_ref.extractall(extracted_dir)
#             scan_dir = extracted_dir
#         else:
#             scan_dir = tmp_path

#         # --- Step 2: Walk through the extracted directory ---
#         print(f"[TestCoverageAgent] Walking directory: {scan_dir}")
#         for root, _, files in os.walk(scan_dir):
#             for file in files:
#                 # Identify likely test files
#                 if "test" in file.lower() and file.endswith((".py", ".java", ".js", ".ts")):
#                     file_path = os.path.join(root, file)
#                     print(f"[TestCoverageAgent] Found test file: {file_path}")
#                     try:
#                         with open(file_path, "r", encoding="utf-8") as f:
#                             content = f.read()
#                         test_excerpt = content[:2000]  # limit size
#                         test_details.append({
#                             "file": file,
#                             "excerpt": test_excerpt
#                         })
#                     except Exception as e:
#                         test_details.append({
#                             "file": file,
#                             "error": str(e)
#                         })

#         # --- Step 3: Cleanup temp extracted folder (optional) ---
#         if extracted_dir:
#             shutil.rmtree(extracted_dir, ignore_errors=True)

#         print(test_details)

#         # --- Step 4: Prepare LLM prompt ---
#         prompt = f"""
# You are a Test Coverage Evaluation Agent.

# You are given:
# 1. A project description.
# 2. Extracted test cases.

# Your goal:
# - Check if the project description provides enough information for a developer
#   to understand and implement code that passes all test cases.
# - Identify missing or unclear specifications (e.g., input/output not defined, function names missing, logic not described).
# - Assess the alignment between test expectations and description content.

# Return JSON:
# {{
#   "coverage_score": "<0-100>",
#   "missing_details": ["..."],
#   "remarks": "summary of coverage gaps",
#   "suggestions": ["..."]
# }}

# Project Description:
# ---
# {description}
# ---

# Extracted Test Files Summary:
# ---
# {test_details}
# ---
# """
#         return self.run_prompt(prompt)


# from agents.base_agent import BaseAgent
# import os
# import zipfile
# import tempfile
# import shutil

# class TestCoverageAgent(BaseAgent):
#     def analyze(self, description: str, tmp_path: str, results: dict = None):
#         """
#         Analyze whether the project description provides enough details
#         to implement and pass all test cases found under tmp_path.
#         Automatically extracts .zip files before scanning.
#         Optionally uses previous agent results for context.
#         """
#         print(f"[TestCoverageAgent] Scanning boilerplate at {tmp_path} for test cases.")
#         test_details = []

#         # --- Step 1: Detect and extract zip ---
#         extracted_dir = None
#         if tmp_path.endswith(".zip") or (
#             os.path.isdir(tmp_path)
#             and any(f.endswith(".zip") for f in os.listdir(tmp_path))
#         ):
#             zip_file_path = tmp_path
#             # If tmp_path is a directory containing the zip, locate it
#             if os.path.isdir(tmp_path):
#                 for f in os.listdir(tmp_path):
#                     if f.endswith(".zip"):
#                         zip_file_path = os.path.join(tmp_path, f)
#                         break

#             extracted_dir = tempfile.mkdtemp()
#             print(f"[TestCoverageAgent] Extracting zip {zip_file_path} → {extracted_dir}")
#             with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
#                 zip_ref.extractall(extracted_dir)
#             scan_dir = extracted_dir
#         else:
#             scan_dir = tmp_path

#         # --- Step 2: Walk through the extracted directory ---
#         print(f"[TestCoverageAgent] Walking directory: {scan_dir}")
#         for root, _, files in os.walk(scan_dir):
#             for file in files:
#                 # Identify likely test files
#                 if "test" in file.lower() and file.endswith((".py", ".java", ".js", ".ts")):
#                     file_path = os.path.join(root, file)
#                     print(f"[TestCoverageAgent] Found test file: {file_path}")
#                     try:
#                         with open(file_path, "r", encoding="utf-8") as f:
#                             content = f.read()
#                         test_excerpt = content[:2000]  # limit size
#                         test_details.append({
#                             "file": file,
#                             "excerpt": test_excerpt
#                         })
#                     except Exception as e:
#                         test_details.append({
#                             "file": file,
#                             "error": str(e)
#                         })

#         # --- Step 3: Cleanup temp extracted folder ---
#         if extracted_dir:
#             shutil.rmtree(extracted_dir, ignore_errors=True)
        
#         print(test_details)

#         # --- Step 4: Prepare LLM prompt ---
#         prompt = f"""
# You are a Test Coverage Evaluation Agent.

# You are given:
# 1. A project description.
# 2. Extracted test cases.

# Your goal:
# - Check if the project description provides enough information for a developer
#   to understand and implement code that passes all test cases.
# - Identify missing or unclear specifications (e.g., input/output not defined, function names missing, logic not described).
# - Assess the alignment between test expectations and description content.

# Return JSON:
# {{
#   "coverage_score": "<0-100>",
#   "missing_details": ["..."],
#   "remarks": "summary of coverage gaps",
#   "suggestions": ["..."]
# }}

# Project Description:
# ---
# {description}
# ---

# Extracted Test Files Summary:
# ---
# {test_details}
# ---
# """
#         return self.run_prompt(prompt)

import re
from agents.base_agent import BaseAgent
import os, zipfile, tempfile, shutil, json

class TestCoverageAgent(BaseAgent):
#     def extract_testcases_with_llm(self, file_content: str, file_name: str):
#         """
#         Ask the LLM to extract all individual testcases from the file.
#         Return a list of dicts: [{ test_name, test_body }]
#         """
#         print(f"[TestCoverageAgent] Extracting testcases from {file_name} using LLM.")
#         print(f"[TestCoverageAgent] File content length: {file_content} characters.")
#         prompt = f"""
# You are a Test Extraction Assistant.

# Extract **all individual testcases** from the following test file.
# Each testcase should have:
# - "test_name": a short, meaningful name (from function name or description)
# - "test_body": the full content of that test

# Return valid JSON as a list:
# [
#   {{ "test_name": "...", "test_body": "..." }},
#   ...
# ]

# File name: {file_name}

# File content:
# ---
# {file_content[:6000]}
# ---
# """
#         response = self.run_prompt(prompt)

#         # Try to parse JSON output from LLM safely
#         try:
#             parsed = json.loads(response)
#             if isinstance(parsed, list):
#                 return parsed
#             elif isinstance(parsed, dict) and "testcases" in parsed:
#                 return parsed["testcases"]
#         except Exception:
#             print("[TestCoverageAgent] ⚠️ Could not parse LLM response as JSON, returning empty.")
#             return []
#         return []

#     def extract_testcases_with_llm(self, file_content: str, file_name: str):
#         """
#         Ask the LLM to extract all individual testcases from the file.
#         Returns a list of dicts: [{ test_name, test_body }]
#         """
#         print(f"[TestCoverageAgent] Extracting testcases from {file_name} using LLM.")
#         print(f"[TestCoverageAgent] File content length: {len(file_content)} characters.")

#         prompt = f"""
# You are a Test Extraction Assistant.

# Extract **all individual testcases** from the following test file.
# Each testcase should have:
# - "test_name": a short, meaningful name (from function name or description)
# - "test_body": the full content of that test

# Return only valid JSON as a list:
# [
#   {{ "test_name": "...", "test_body": "..." }},
#   ...
# ]

# File name: {file_name}

# File content:
# ---
# {file_content}
# ---
# """

#         response = self.run_prompt_test_extract(prompt)
#         print(f"[TestCoverageAgent] LLM response type: {response}")

#         # If the model returned a dict with an error, handle gracefully
#         if isinstance(response, dict) and "status" in response and response["status"] == "error":
#             print(f"[TestCoverageAgent] ⚠️ LLM error: {response['error']}")
#             return []

#         # Directly return parsed response if it's a list of testcases
#         if isinstance(response, list):
#             return response

#         # If the LLM wrapped testcases inside a dict
#         if isinstance(response, dict) and "testcases" in response:
#             return response["testcases"]

#         print("[TestCoverageAgent] ⚠️ Unexpected LLM output, returning empty list.")
#         return []




#     def analyze(self, description: str, tmp_path: str, results: dict = None):
#         print(f"[TestCoverageAgent] Scanning boilerplate at {tmp_path} for test cases.")

#         extracted_dir = None
#         if tmp_path.endswith(".zip"):
#             extracted_dir = tempfile.mkdtemp()
#             with zipfile.ZipFile(tmp_path, "r") as zip_ref:
#                 zip_ref.extractall(extracted_dir)
#             scan_dir = extracted_dir
#         else:
#             scan_dir = tmp_path

#         # --- Step 1: Identify test files ---
#         all_testcases = []
#         for root, _, files in os.walk(scan_dir):
#             for file in files:
#                 if "test" in file.lower() and file.endswith((".py", ".java", ".js", ".ts")):
#                     file_path = os.path.join(root, file)
#                     print(f"[TestCoverageAgent] Processing file: {file_path}")

#                     try:
#                         with open(file_path, "r", encoding="utf-8") as f:
#                             content = f.read()
#                         extracted = self.extract_testcases_with_llm(content, file)
#                         print(f"[TestCoverageAgent] Extracted {extracted} testcases from {file}")
#                         for t in extracted:
#                             t["file"] = file
#                         all_testcases.extend(extracted)
#                     except Exception as e:
#                         print(f"[TestCoverageAgent] Error reading file {file_path}: {e}")

#         print(f"[TestCoverageAgent] Total testcases found: {len(all_testcases)}")

#         # --- Step 2: LLM coverage check for each testcase ---
#         results_list = []
#         for t in all_testcases:
#             test_name = t.get("test_name", "unknown")
#             test_body = t.get("test_body", "")
#             file = t.get("file", "")

#             prompt = f"""
# You are a **Test Coverage Evaluation Agent**.

# You are given:
# - Project description
# - One test case from `{file}`

# Check whether the project description provides all the details necessary to
# implement code that passes this test.

# Focus only on this single test.

# Return valid JSON:
# {{
#   "file": "{file}",
#   "test_name": "{test_name}",
#   "coverage_score": "<0-100>",
#   "missing_details": ["..."],
#   "remarks": "summary of coverage gaps"
# }}

# Project Description:
# ---
# {description}
# ---

# Test Case:
# ---
# {test_body[:2000]}
# ---
# """
#             res = self.run_prompt(prompt)
#             results_list.append(res)

#         # --- Step 3: Aggregate results ---
#         total = 0
#         count = 0
#         all_missing = []

#         for res in results_list:
#             try:
#                 r = json.loads(res)
#                 score = int(r.get("coverage_score", 0))
#                 total += score
#                 count += 1
#                 all_missing.extend(r.get("missing_details", []))
#             except Exception:
#                 continue

#         avg = round(total / count, 2) if count else 0
#         final = {
#             "overall_coverage_score": avg,
#             "missing_details_summary": list(set(all_missing)),
#             "individual_testcases": results_list
#         }

#         if extracted_dir:
#             shutil.rmtree(extracted_dir, ignore_errors=True)

#         return final
        
    def extract_testcases_with_llm(self, file_content: str, file_name: str):
        """
        Ask the LLM to extract all individual testcases from the file.
        Return a list of dicts: [{ test_name, test_body }]
        """
        print(f"[TestCoverageAgent] Extracting testcases from {file_name} using LLM.")
        print(f"[TestCoverageAgent] File content length: {len(file_content)} characters.")

        prompt = f"""
You are a Test Extraction Assistant.

Extract **all individual testcases** from the following test file.
Each testcase should have:
- "test_name": a short, meaningful name (from function name or description)
- "test_body": the full content of that test

Return ONLY valid JSON as a list:
[
  {{ "test_name": "...", "test_body": "..." }},
  ...
]

Do not include explanations, markdown formatting, or comments.

File name: {file_name}

File content:
---
{file_content}
---
"""

        llm_response = self.run_prompt_test_extract(prompt)
        print(f"[TestCoverageAgent] Raw LLM response type: {type(llm_response)}")
        print(llm_response)

        # Handle both dicts or raw strings
        if isinstance(llm_response, dict) and "raw" in llm_response:
            text = llm_response["raw"]
        elif isinstance(llm_response, str):
            text = llm_response
        else:
            text = json.dumps(llm_response)

        # Try to extract valid JSON from noisy content
        json_match = re.search(r"\[\s*{[\s\S]*}\s*\]", text)
        # if not json_match:
        #     print("[TestCoverageAgent] ⚠️ Could not find JSON array in LLM output.")
        #     return []

        # json_str = json_match.group(0)
        # # Replace problematic control chars
        # json_str = json_str.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")

        # try:
        #     parsed = json.loads(json_str)
        #     if isinstance(parsed, list):
        #         print(f"[TestCoverageAgent] ✅ Extracted {len(parsed)} testcases successfully.")
        #         return parsed
        #     else:
        #         print("[TestCoverageAgent] ⚠️ Parsed JSON was not a list.")
        #         return []
        # except Exception as e:
        #     print(f"[TestCoverageAgent] ⚠️ JSON parse failed: {e}")
        #     with open("debug_test_extraction_output.json", "w") as f:
        #         f.write(json_str)
        #     return []
        if not json_match:
            print("[TestCoverageAgent] ⚠️ Could not find JSON array in LLM output.")
            with open("debug_test_extraction_output.txt", "w") as f:
                f.write(clean_text)
            return []

        json_str = json_match.group(0)

        # Sanitize common formatting noise
        json_str = json_str.encode("utf-8", "ignore").decode("utf-8")
        json_str = json_str.replace("\r", "").replace("\t", " ")
        json_str = re.sub(r"\\+", "\\\\", json_str)

        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                print(f"[TestCoverageAgent] ✅ Extracted {len(parsed)} testcases successfully.")
                return parsed
        except Exception as e:
            print(f"[TestCoverageAgent] ⚠️ JSON parse failed after cleaning: {e}")
            with open("debug_test_extraction_output.json", "w") as f:
                f.write(json_str)
            return []

    # ------------------------------------------------------------------------

    def analyze(self, description: str, tmp_path: str, results: dict = None):
        """
        Main entrypoint: Analyze how well the description covers the given testcases.
        """
        print(f"[TestCoverageAgent] Scanning boilerplate at {tmp_path} for test files.")
        extracted_dir = None
        all_test_coverage = []

        # --- Step 1: Detect and extract zip ---
        if tmp_path.endswith(".zip") or (
            os.path.isdir(tmp_path) and any(f.endswith(".zip") for f in os.listdir(tmp_path))
        ):
            zip_file_path = tmp_path
            if os.path.isdir(tmp_path):
                for f in os.listdir(tmp_path):
                    if f.endswith(".zip"):
                        zip_file_path = os.path.join(tmp_path, f)
                        break

            extracted_dir = tempfile.mkdtemp()
            print(f"[TestCoverageAgent] Extracting zip {zip_file_path} → {extracted_dir}")
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(extracted_dir)
            scan_dir = extracted_dir
        else:
            scan_dir = tmp_path

        # --- Step 2: Find test files ---
        test_files = []
        for root, _, files in os.walk(scan_dir):
            for f in files:
                if "test" in f.lower() and f.endswith((".py", ".java", ".js", ".ts", ".cs")):
                    test_files.append(os.path.join(root, f))

        print(f"[TestCoverageAgent] Found {len(test_files)} test files.")

        # --- Step 3: Extract testcases and evaluate each ---
        for test_file in test_files:
            print(f"[TestCoverageAgent] Processing {test_file}")
            try:
                with open(test_file, "r", encoding="utf-8") as f:
                    content = f.read()

                testcases = self.extract_testcases_with_llm(content, os.path.basename(test_file))
                print(f"[TestCoverageAgent] Extracted {len(testcases)} testcases from {test_file}")

                for tc in testcases:
                    test_name = tc.get("test_name", "unknown")
                    test_body = tc.get("test_body", "")

                    # Ask LLM if description covers this testcase
                    coverage_prompt = f"""
You are a Test Coverage Evaluator.

Check whether the project description provides all the necessary information
for implementing the following testcase.

Project Description:
---
{description}
---

Testcase Name: {test_name}
Testcase Code:
---
{test_body}
---

Return JSON:
{{
  "test_name": "{test_name}",
  "is_covered": true/false,
  "missing_info": ["..."],
  "reason": "why covered or not"
}}
"""
                    result = self.run_prompt(coverage_prompt)
                    all_test_coverage.append(result)

            except Exception as e:
                all_test_coverage.append({"file": test_file, "error": str(e)})

        # --- Step 4: Cleanup ---
        if extracted_dir:
            shutil.rmtree(extracted_dir, ignore_errors=True)

        # --- Step 5: Aggregate coverage score ---
        valid_results = [r for r in all_test_coverage if isinstance(r, dict) and "is_covered" in r]
        if valid_results:
            score = int(
                (sum(1 for r in valid_results if r.get("is_covered")) / len(valid_results)) * 100
            )
        else:
            score = 0

        missing_details = []
        for r in valid_results:
            if not r.get("is_covered") and "missing_info" in r:
                missing_details.extend(r["missing_info"])

        report = {
            "coverage_score": score,
            "total_tests": len(valid_results),
            "missing_details": list(set(missing_details)),
            "remarks": f"{score}% of testcases appear covered by description.",
            "per_test_details": all_test_coverage,
        }

        print(f"[TestCoverageAgent] Final Coverage Report: {json.dumps(report, indent=2)}")
        return report