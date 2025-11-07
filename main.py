# from fastapi import FastAPI, UploadFile, File, Form
# import tempfile
# import os
# import asyncio
# import json
# import orchestrator
# from qc_graph.qc_flow import QCGraph
# from starlette.responses import StreamingResponse

# app = FastAPI(title="AI QC System")

# qc_graph = QCGraph()

# async def run_qc_task(description: str):
#     return await asyncio.to_thread(qc_graph.execute, description)

# orch = orchestrator.Orchestrator()

# async def run_docker_task(zip_file_path: str, config_json: dict, project_description: str):
#     return await asyncio.to_thread(orch.build_and_run_docker, zip_file_path, config_json, project_description)

# @app.post("/qc/full-run")
# async def qc_full_run(
#     description: str = Form(..., description="Project description text"),
#     zip_file: UploadFile = File(..., description="Project boilerplate zip file"),
#     config: str = Form(..., description="Config JSON as string for testcases")
# ):
#     try:
#         config_json = json.loads(config)
#     except Exception as e:
#         return {"error": f"Invalid config JSON: {str(e)}"}

#     with tempfile.TemporaryDirectory() as tmp_dir:
#         tmp_path = os.path.join(tmp_dir, zip_file.filename)
#         with open(tmp_path, "wb") as f:
#             f.write(await zip_file.read())

#         qc_task = run_qc_task(description)
#         docker_task = run_docker_task(tmp_path, config_json, description)
#         qc_result, docker_result = await asyncio.gather(qc_task,docker_task)

#     return {
#         "status": "completed",
#         "qc_results": qc_result,
#         "docker_results": docker_result
#     }

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from starlette.responses import StreamingResponse
import tempfile
import os
import asyncio
import json
import orchestrator
from qc_graph.qc_flow import QCGraph

app = FastAPI(title="AI QC System")

# CORS: allow cross-origin requests. Change `origins` to restrict in production.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

qc_graph = QCGraph()
orch = orchestrator.Orchestrator()


async def run_qc_task(description: str, tmp_path: str):
    return await asyncio.to_thread(qc_graph.execute, description, tmp_path)


async def run_docker_task(zip_file_path: str, config_json: dict, project_description: str):
    return await asyncio.to_thread(orch.build_and_run_docker, zip_file_path, config_json, project_description)


@app.post("/qc/full-run")
async def qc_full_run(
    description: str = Form(..., description="Project description text"),
    zip_file: UploadFile = File(..., description="Project boilerplate zip file"),
    config: str = Form(..., description="Config JSON as string for testcases")
):
    # Step 1: Parse config early
    try:
        config_json = json.loads(config)
    except Exception as e:
        return {"error": f"Invalid config JSON: {str(e)}"}

    # Step 2: Read the uploaded file completely here (before StreamingResponse starts)
    zip_bytes = await zip_file.read()
    zip_filename = zip_file.filename

    async def event_stream():
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = os.path.join(tmp_dir, zip_filename)

            # Write the zip file bytes to a temp path
            with open(tmp_path, "wb") as f:
                f.write(zip_bytes)

            # Start both tasks
            qc_task = asyncio.create_task(run_qc_task(description, tmp_path))
            # docker_task = asyncio.create_task(run_docker_task(tmp_path, config_json, description))

            # Wait for QC first
            qc_result = await qc_task
            yield f"data: {json.dumps({'stage': 'qc_completed', 'qc_results': qc_result})}\n\n"

            # Then Docker
            # docker_result = await docker_task
            # yield f"data: {json.dumps({'stage': 'docker_completed', 'docker_results': docker_result})}\n\n"

            yield f"data: {json.dumps({'stage': 'completed'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# -------------------------
# /fetch-qbs endpoint
# -------------------------
@app.post("/fetch-qbs")
async def fetch_qbs(request: Request):
    """
    Fetches Question Banks from Examly API using an Auth Token.
    Body Params:
        - authToken: str (in body or query)
        - search: str (optional)
    """
    data = await request.json()
    auth_token = data.get("authToken") or request.query_params.get("authToken")
    search_term = data.get("search", "")

    if not auth_token:
        return JSONResponse({"error": "Auth token is required"}, status_code=400)

    url = "https://api.examly.io/api/v2/questionbanks"
    payload = {
        "branch_id": "all",
        "search": search_term,
        "limit": 5000,
        "page": 1,
        "visibility": "All",
        "mainDepartmentUser": True,
        "department_id": [
            "617346bd-b9c8-468d-9099-12170fb3b570",
            "8c9bb195-1e81-4506-bc39-c48e6450c2a0"
        ]
    }
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            qbs = response.json()
            return JSONResponse(qbs)
    except httpx.HTTPStatusError as e:
        print("Error fetching QBs:", e.response.text)
        return JSONResponse({"error": "Failed to fetch QBs", "details": e.response.text}, status_code=500)
    except Exception as e:
        print("Error fetching QBs:", str(e))
        return JSONResponse({"error": "Unexpected error", "details": str(e)}, status_code=500)