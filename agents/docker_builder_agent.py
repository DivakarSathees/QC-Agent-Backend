# agents/docker_builder_agent.py
import os
import tempfile
import docker
import shutil
import zipfile
import uuid
from typing import Dict

class DockerBuilderAgent:
    def __init__(self, base_image="mcr.microsoft.com/dotnet/sdk:6.0"):
        self.base_image = base_image
        self.client = docker.from_env()

    def build_image_with_boilerplate(self, zip_file_path: str, image_tag: str = None, solution_dir: str = None) -> Dict:
        """
        Build a docker image that contains the boilerplate zip.
        Returns: {"image_tag": ..., "status": "success/failure", "logs": "..."}
        """
        image_tag = image_tag or f"project_image_{uuid.uuid4().hex[:8]}"
        temp_dir = tempfile.mkdtemp()
        print(f"[DockerBuilderAgent] Building image with tag: {image_tag}")
        print(solution_dir)
        try:
            # Copy zip to temp
            boilerplate_name = os.path.basename(zip_file_path)
            target_zip = os.path.join(temp_dir, boilerplate_name)
            shutil.copy(zip_file_path, target_zip)

            # Create Dockerfile
            dockerfile_path = os.path.join(temp_dir, "Dockerfile")
            with open(dockerfile_path, "w") as f:
                f.write(f"""
FROM {self.base_image}

# Install unzip if missing
RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /home/coder/project/workspace

# Copy boilerplate zip
COPY {boilerplate_name} /home/coder/project/workspace/{boilerplate_name}

# Unzip boilerplate
RUN unzip {boilerplate_name} -d /home/coder/project/workspace/boilerplate

# after unzip /home/coder/project/workspace/boilerplate/servicerequestscaffolding# ls
# dotnetapp  nunit
# i need directory like /home/coder/project/workspace/dotnetapp and /home/coder/project/workspace/nunit

RUN if [ -d /home/coder/project/workspace/boilerplate/servicerequestscaffolding ]; then \\
      mv /home/coder/project/workspace/boilerplate/servicerequestscaffolding/* /home/coder/project/workspace/ || true; \\
    fi

RUN for d in /home/coder/project/workspace/boilerplate/*; do \\
      if [ -d "$d" ]; then \\
        mv "$d" /home/coder/project/workspace/ || true; \\
      fi; \\
    done

# Default workdir
WORKDIR /home/coder/project/workspace/
""")
        #     # Build the image
        #     logs = self.client.images.build(path=temp_dir, tag=image_tag, rm=True)
        #     print(logs) # For debugging
        #     return {"status": "success", "image_tag": image_tag, "logs": str(logs)}
        # except Exception as e:
        #     return {"status": "failure", "error": str(e)}
        # finally:
        #     shutil.rmtree(temp_dir)
                if solution_dir and os.path.exists(solution_dir):
                    f.write(f"""
    # Copy AI-generated solution files
    COPY solution/ /home/coder/project/workspace/
    """)

                f.write("""
    # Set working directory
    WORKDIR /home/coder/project/workspace/
    """)

            # If solution exists, copy it into temp_dir so Docker build can access it
            if solution_dir and os.path.exists(solution_dir):
                print(f"[DockerBuilderAgent] Copying AI solution from {solution_dir} to Docker context...")
                target_solution = os.path.join(temp_dir, "solution")
                shutil.copytree(solution_dir, target_solution)

            print(f"[DockerBuilderAgent] Building image {image_tag} ...")
            image, logs = self.client.images.build(path=temp_dir, tag=image_tag, rm=True)
            print(f"[DockerBuilderAgent] Build logs: {logs}")  # For debugging
            print(f"[DockerBuilderAgent] Successfully built image: {image_tag}")
            print(image)
            return {"status": "success", "image_tag": image_tag, "logs": str(logs)}
        except Exception as e:
            return {"status": "failure", "error": str(e)}
        finally:
                shutil.rmtree(temp_dir, ignore_errors=True)


    def build_image_from_directory(self, directory: str) -> Dict:
        """
        Builds a Docker image directly from a local directory (after AI modifications).
        """
        try:
            tag = f"ai_solution_image"
            print(f"[DockerBuilderAgent] Building new image from directory: {directory}")
            image, logs = self.client.images.build(path=directory, tag=tag)
            return {"status": "success", "image_tag": tag}
        except Exception as e:
            return {"status": "failure", "error": str(e)}

    def run_container(self, image_tag: str, config_json: dict, detach=False) -> Dict:
        """
        Run a container from the given image_tag and execute a command.
        Returns: {"status": "success/failure", "stdout":..., "stderr":...}
        """
        print(config_json)
        print(f"Running container from image: {image_tag} with command: {config_json["config"][0]["testcase_run_command"]}")
        try:
            container = self.client.containers.run(
                image_tag,
                command=config_json["config"][0]["testcase_run_command"],
                detach=detach,
                remove=True,
                tty=True
            )
            if detach:
                return {"status": "success", "container_id": container.id}
            else:
                output = container.decode("utf-8") if isinstance(container, bytes) else str(container)
                return {"status": "success", "output": output}
        except Exception as e:
            return {"status": "failure", "error": str(e)}

    # def run_container(self, image_tag: str, command: str = "sh", detach=False) -> Dict:
        # try:
        #     container = self.client.containers.run(
        #         image_tag,
        #         command=command,
        #         detach=detach,
        #         remove=True,
        #         tty=True
        #     )

        #     if detach:
        #         return {"status": "success", "container_id": container.id}
        #     else:
        #         # container is either bytes (output) or string
        #         if isinstance(container, bytes):
        #             output = container.decode("utf-8")
        #         elif isinstance(container, str):
        #             output = container
        #         else:
        #             # fallback: try logs() if container is a Container object
        #             try:
        #                 output = container.logs().decode("utf-8")
        #             except Exception:
        #                 output = str(container)

        #         return {"status": "success", "output": output}

        # except docker.errors.ContainerError as e:
        #     # capture stderr from the container
        #     return {"status": "failure", "error": f"Container error: {e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else str(e.stderr)}"}
        # except Exception as e:
        #     return {"status": "failure", "error": str(e)}
