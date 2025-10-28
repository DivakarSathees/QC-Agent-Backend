# from agents.docker_builder_agent import DockerBuilderAgent

# # Inside Orchestrator
# def build_and_run_docker(zip_file_path: str,  config_json: dict) -> dict:
#     docker_agent = DockerBuilderAgent()
#     build_res = docker_agent.build_image_with_boilerplate(zip_file_path)
#     if build_res["status"] != "success":
#         return {"status": "build_failed", "details": build_res}

#     image_tag = build_res["image_tag"]
#     # run container with test command inside
#     run_res = docker_agent.run_container(image_tag, config_json=config_json)
#     return {"build_result": build_res, "run_result": run_res}
import os
import shutil
import zipfile
from agents.base_agent import BaseAgent
from agents.docker_builder_agent import DockerBuilderAgent
from agents.solution_writer_agent import SolutionWriterAgent

class Orchestrator:
    def __init__(self, ai_client=None):
        self.ai_client = ai_client or BaseAgent()  
        self.docker_agent = DockerBuilderAgent()
        self.solution_writer = SolutionWriterAgent(ai_client=self.ai_client)
        

    def build_and_run_docker(self, zip_file_path: str, config_json: dict, project_description: str):
        # 1. Build docker image with boilerplate
        build_res = self.docker_agent.build_image_with_boilerplate(zip_file_path)
        if build_res["status"] != "success":
            return {"status": "build_failed", "details": build_res}

        image_tag = build_res["image_tag"]

        # 2. Extract the boilerplate locally to write solution
        current_dir = os.getcwd()
        extract_path = os.path.join(current_dir, "testing")

        if os.path.exists(extract_path):
            print(f"Removing existing directory at: {extract_path}")
            shutil.rmtree(extract_path)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            print(f"Extracting zip file to: {extract_path}")
            zip_ref.extractall(extract_path)

        # ✅ Optional: Auto-detect nested project folder
        subdirs = [os.path.join(extract_path, d) for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d))]
        src_dir = subdirs[0] if len(subdirs) == 1 else extract_path

        print(f"Source directory for solution writing: {src_dir}")

        # 3. Generate code using solution writer agent
        write_summary = self.solution_writer.write_solution(src_dir, project_description)

        final_build = self.docker_agent.build_image_with_boilerplate(
            zip_file_path=zip_file_path,
            solution_dir=src_dir  # 👈 include the updated source
        )
        print(f"[Orchestrator] Final build result: {final_build}")
        if final_build["status"] != "success":
            return {"status": "final_build_failed", "details": final_build}

        # 4. Run docker container with test command
        run_res = self.docker_agent.run_container( final_build["image_tag"], config_json=config_json 
                                                #   ,solution_dir=src_dir 
                                                  )

        # ✅ Don’t delete current_dir; delete only extraction folder
        shutil.rmtree(extract_path)

        return {
            "build_result": build_res,
            "solution_summary": write_summary,
            "run_result": run_res
        }
