from fastapi import FastAPI, UploadFile, File, Form
import tempfile
import os
import asyncio
import json
import orchestrator
from qc_graph.qc_flow import QCGraph

app = FastAPI(title="AI QC System")

qc_graph = QCGraph()

async def run_qc_task(description: str):
    return await asyncio.to_thread(qc_graph.execute, description)

orch = orchestrator.Orchestrator()

async def run_docker_task(zip_file_path: str, config_json: dict, project_description: str):
    return await asyncio.to_thread(orch.build_and_run_docker, zip_file_path, config_json, project_description)

@app.post("/qc/full-run")
async def qc_full_run(
    description: str = Form(..., description="Project description text"),
    zip_file: UploadFile = File(..., description="Project boilerplate zip file"),
    config: str = Form(..., description="Config JSON as string for testcases")
):
    try:
        config_json = json.loads(config)
    except Exception as e:
        return {"error": f"Invalid config JSON: {str(e)}"}

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = os.path.join(tmp_dir, zip_file.filename)
        with open(tmp_path, "wb") as f:
            f.write(await zip_file.read())

        qc_task = run_qc_task(description)
        docker_task = run_docker_task(tmp_path, config_json, description)
        qc_result, docker_result = await asyncio.gather(qc_task,docker_task)

    return {
        "status": "completed",
        "qc_results": qc_result,
        "docker_results": docker_result
    }
