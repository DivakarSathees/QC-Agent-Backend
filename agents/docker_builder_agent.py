# # agents/docker_builder_agent.py
# import os
# import tempfile
# import docker
# import shutil
# import zipfile
# import uuid
# from typing import Dict

# class DockerBuilderAgent:
#     def __init__(self, base_image="mcr.microsoft.com/dotnet/sdk:6.0"):
#         self.base_image = base_image
#         self.client = docker.from_env()

#     def build_image_with_boilerplate(self, zip_file_path: str, image_tag: str = None, solution_dir: str = None) -> Dict:
#         """
#         Build a docker image that contains the boilerplate zip.
#         Returns: {"image_tag": ..., "status": "success/failure", "logs": "..."}
#         """
#         image_tag = image_tag or f"project_image_{uuid.uuid4().hex[:8]}"
#         temp_dir = tempfile.mkdtemp()
#         print(f"[DockerBuilderAgent] Building image with tag: {image_tag}")
#         print(solution_dir)
#         try:
#             # Copy zip to temp
#             boilerplate_name = os.path.basename(zip_file_path)
#             target_zip = os.path.join(temp_dir, boilerplate_name)
#             shutil.copy(zip_file_path, target_zip)

#             # Create Dockerfile
#             dockerfile_path = os.path.join(temp_dir, "Dockerfile")
#             with open(dockerfile_path, "w") as f:
#                 f.write(f"""
# FROM {self.base_image}

# # Install unzip if missing
# RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*

# # Create workspace
# WORKDIR /home/coder/project/workspace

# # Copy boilerplate zip
# COPY {boilerplate_name} /home/coder/project/workspace/{boilerplate_name}

# # Unzip boilerplate
# RUN unzip {boilerplate_name} -d /home/coder/project/workspace/boilerplate

# # after unzip /home/coder/project/workspace/boilerplate/servicerequestscaffolding# ls
# # dotnetapp  nunit
# # i need directory like /home/coder/project/workspace/dotnetapp and /home/coder/project/workspace/nunit

# RUN if [ -d /home/coder/project/workspace/boilerplate/servicerequestscaffolding ]; then \\
#       mv /home/coder/project/workspace/boilerplate/servicerequestscaffolding/* /home/coder/project/workspace/ || true; \\
#     fi

# RUN for d in /home/coder/project/workspace/boilerplate/*; do \\
#       if [ -d "$d" ]; then \\
#         mv "$d" /home/coder/project/workspace/ || true; \\
#       fi; \\
#     done

# # Default workdir
# WORKDIR /home/coder/project/workspace/
# """)
#         #     # Build the image
#         #     logs = self.client.images.build(path=temp_dir, tag=image_tag, rm=True)
#         #     print(logs) # For debugging
#         #     return {"status": "success", "image_tag": image_tag, "logs": str(logs)}
#         # except Exception as e:
#         #     return {"status": "failure", "error": str(e)}
#         # finally:
#         #     shutil.rmtree(temp_dir)
#                 if solution_dir and os.path.exists(solution_dir):
#                     f.write(f"""
#     # Copy AI-generated solution files
#     COPY solution/ /home/coder/project/workspace/
#     """)

#                 f.write("""
#     # Set working directory
#     WORKDIR /home/coder/project/workspace/
#     """)

#             # If solution exists, copy it into temp_dir so Docker build can access it
#             if solution_dir and os.path.exists(solution_dir):
#                 print(f"[DockerBuilderAgent] Copying AI solution from {solution_dir} to Docker context...")
#                 target_solution = os.path.join(temp_dir, "solution")
#                 shutil.copytree(solution_dir, target_solution)

#             print(f"[DockerBuilderAgent] Building image {image_tag} ...")
#             image, logs = self.client.images.build(path=temp_dir, tag=image_tag, rm=True)
#             print(f"[DockerBuilderAgent] Build logs: {logs}")  # For debugging
#             print(f"[DockerBuilderAgent] Successfully built image: {image_tag}")
#             print(image)
#             return {"status": "success", "image_tag": image_tag, "logs": str(logs)}
#         except Exception as e:
#             return {"status": "failure", "error": str(e)}
#         finally:
#                 shutil.rmtree(temp_dir, ignore_errors=True)


#     def build_image_from_directory(self, directory: str) -> Dict:
#         """
#         Builds a Docker image directly from a local directory (after AI modifications).
#         """
#         try:
#             tag = f"ai_solution_image"
#             print(f"[DockerBuilderAgent] Building new image from directory: {directory}")
#             image, logs = self.client.images.build(path=directory, tag=tag)
#             return {"status": "success", "image_tag": tag}
#         except Exception as e:
#             return {"status": "failure", "error": str(e)}

#     def run_container(self, image_tag: str, config_json: dict, detach=False) -> Dict:
#         """
#         Run a container from the given image_tag and execute a command.
#         Returns: {"status": "success/failure", "stdout":..., "stderr":...}
#         """
#         print(config_json)
#         print(f"Running container from image: {image_tag} with command: {config_json["config"][0]["testcase_run_command"]}")
#         try:
#             container = self.client.containers.run(
#                 image_tag,
#                 command=config_json["config"][0]["testcase_run_command"],
#                 detach=detach,
#                 remove=True,
#                 tty=True
#             )
#             if detach:
#                 return {"status": "success", "container_id": container.id}
#             else:
#                 output = container.decode("utf-8") if isinstance(container, bytes) else str(container)
#                 return {"status": "success", "output": output}
#         except Exception as e:
#             return {"status": "failure", "error": str(e)}

# agents/docker_builder_agent.py
import os
import tempfile
import docker
import shutil
import zipfile
import uuid
from typing import Dict

class DockerBuilderAgent:
    def __init__(self, language="dotnet"):
        self.language = language
        self.client = docker.from_env()

        # Default base images per language
        self.base_images = {
            "dotnet": "mcr.microsoft.com/dotnet/sdk:6.0",
            "java": "gcr.io/examly-dev/vscodejavamysqlseventeen"
        }

    def build_image_with_boilerplate(self, zip_file_path: str, image_tag: str = None, solution_dir: str = None) -> Dict:
        image_tag = image_tag or f"project_image_{uuid.uuid4().hex[:8]}"
        temp_dir = tempfile.mkdtemp()
        print(solution_dir)
        print(f"[DockerBuilderAgent] Building image with tag: {image_tag} for language: {self.language}")
        try:
            boilerplate_name = os.path.basename(zip_file_path)
            target_zip = os.path.join(temp_dir, boilerplate_name)
            shutil.copy(zip_file_path, target_zip)

            dockerfile_path = os.path.join(temp_dir, "Dockerfile")

#             if self.language == "java":
#                 print("[DockerBuilderAgent] Using full Java Docker setup...")
#                 with open(dockerfile_path, "w") as f:
# #                     f.write(f"""
# # # ===== JAVA BASE ENVIRONMENT =====
# # # FROM {self.base_images["java"]}
# # FROM openjdk:17-slim

# # # Install unzip if missing
# # RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*

# # # Create workspace
# # WORKDIR /home/coder/project/workspace

# # # Copy boilerplate zip
# # COPY {boilerplate_name} /home/coder/project/workspace/{boilerplate_name}

# # # Unzip boilerplate
# # RUN unzip {boilerplate_name} -d /home/coder/project/workspace/boilerplate

# # # after unzip /home/coder/project/workspace/boilerplate/servicerequestscaffolding# ls
# # # dotnetapp  nunit
# # # i need directory like /home/coder/project/workspace/dotnetapp and /home/coder/project/workspace/nunit

# # RUN if [ -d /home/coder/project/workspace/boilerplate/servicerequestscaffolding ]; then \\
# #       mv /home/coder/project/workspace/boilerplate/servicerequestscaffolding/* /home/coder/project/workspace/ || true; \\
# #     fi

# # RUN for d in /home/coder/project/workspace/boilerplate/*; do \\
# #       if [ -d "$d" ]; then \\
# #         mv "$d" /home/coder/project/workspace/ || true; \\
# #       fi; \\
# #     done

# # # Default workdir
# # WORKDIR /home/coder/project/workspace/
# # """)
# #                     if solution_dir and os.path.exists(solution_dir):
# #                         f.write("COPY solution/ /home/coder/project/workspace/\n")

# #                     # Append your entire Java base environment setup
# #                     f.write("""
# # # ===== ENVIRONMENT SETUP =====
# # # RUN lsb_release -a
# # RUN apt-get update && \
# #     apt-get --no-install-recommends install -y software-properties-common && \
# #     apt-get clean
# # RUN mkdir -p /home/coder/project && chown -R 1000:1000 /home/coder/project
# # RUN apt-get update && \
# #   apt-get --no-install-recommends -yq install default-mysql-client maven && apt-get clean

# # EXPOSE 3000 8081 8080
# # ENV PORT 3000
# # USER root
# # RUN rm /bin/sh && ln -s /bin/bash /bin/sh
# # RUN apt-get update && \
# #     apt-get --no-install-recommends install -y openjdk-17-jdk && \
# #     apt-get clean
# # # RUN echo "coder:neouser@123" | chpasswd
# # # RUN usermod -aG sudo coder
# # # RUN rm /etc/sudoers.d/nopasswd

# # # nvm environment variables
# # ENV NVM_DIR /usr/local/nvm
# # ENV NODE_VERSION_12 12.22.1
# # ENV NODE_VERSION_14 14.17.1
# # ENV NODE_VERSION_16 16.4.0
# # ENV NODE_VERSION_18 18.20.4
# # ENV NODE_VERSION_20 20.9.0

# # # install nvm
# # RUN curl --silent -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.2/install.sh | bash

# # # install multiple Node versions
# # RUN source "$NVM_DIR"/nvm.sh \\
# #     && nvm install "$NODE_VERSION_12" \\
# #     && nvm install "$NODE_VERSION_14" \\
# #     && nvm install "$NODE_VERSION_16" \\
# #     && nvm install "$NODE_VERSION_18" \\
# #     && nvm install "$NODE_VERSION_20" \\
# #     && nvm alias default "$NODE_VERSION_14" \\
# #     && nvm use default

# # # add node/npm to PATH
# # ENV NODE_PATH $NVM_DIR/v$NODE_VERSION_14/lib/node_modules
# # ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION_14/bin:$PATH

# # # confirm installations
# # RUN node -v
# # RUN npm -v
# # ADD ../common/package.json  /
# # RUN npm install --ignore-scripts

# # RUN apt-get install chromium -y
# # ENV CHROME_BIN=/usr/bin/chromium
# # RUN echo "export CHROME_BIN=/usr/bin/chromium" >> /home/coder/.bashrc

# # USER coder
# # RUN code-server --install-extension vscjava.vscode-spring-initializr
# # RUN code-server --install-extension Angular.ng-template
# # RUN code-server --install-extension cweijan.vscode-mysql-client2
# # RUN code-server --install-extension dsznajder.es7-react-js-snippets
# # RUN code-server --install-extension johnpapa.angular2
# # RUN code-server --install-extension pivotal.vscode-boot-dev-pack
# # RUN code-server --install-extension redhat.java
# # RUN code-server --install-extension sonarsource.sonarlint-vscode
# # RUN code-server --install-extension visualstudioexptteam.vscodeintellicode
# # RUN code-server --install-extension vscjava.vscode-java-debug
# # RUN code-server --install-extension vscjava.vscode-java-dependency
# # RUN code-server --install-extension vscjava.vscode-maven
# # RUN code-server --install-extension vscjava.vscode-java-pack
# # RUN code-server --install-extension vscjava.vscode-java-test
# # RUN code-server --install-extension rangav.vscode-thunder-client

# # # Inject JS modifications
# # COPY ./modification/* /usr/lib/code-server/lib/vscode/out/vs/code/browser/workbench/

# # WORKDIR /home/coder/project/workspace
# # ENV PATH /node_modules/karma-cli/bin:$PATH
# # ENV SHELL /bin/bash
# # RUN echo "source $NVM_DIR/nvm.sh" >> ~/.bashrc
# # ENTRYPOINT dumb-init fixuid -q /usr/bin/code-server --auth none --disable-file-downloads --disable-file-uploads --bind-addr 0.0.0.0:3000 /home/coder/project/workspace
# # """)
#                     f.write(f"""
# # ===== JAVA BASE ENVIRONMENT =====
# FROM openjdk:17-slim

# # Install base dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#       unzip \
#       curl \
#       gnupg \
#       apt-transport-https \
#       software-properties-common \
#       default-mysql-client \
#       maven \
#       chromium \
#       git && \
#     rm -rf /var/lib/apt/lists/*

# # Create workspace
# WORKDIR /home/coder/project/workspace

# # Copy boilerplate zip
# COPY {boilerplate_name} /home/coder/project/workspace/{boilerplate_name}

# # Unzip boilerplate
# RUN unzip {boilerplate_name} -d /home/coder/project/workspace/boilerplate && \
#     if [ -d /home/coder/project/workspace/boilerplate/servicerequestscaffolding ]; then \
#       mv /home/coder/project/workspace/boilerplate/servicerequestscaffolding/* /home/coder/project/workspace/ || true; \
#     fi && \
#     for d in /home/coder/project/workspace/boilerplate/*; do \
#       if [ -d "$d" ]; then \
#         mv "$d" /home/coder/project/workspace/ || true; \
#       fi; \
#     done

# # ===== Node.js 18 via NodeSource (stable + faster than NVM) =====
# # RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
# #     apt-get install -y nodejs && \
# #     npm install -g npm@latest && \
# #     rm -rf /var/lib/apt/lists/*

# # Verify installations
# RUN java -version && mvn -version


# # Copy optional AI-generated solution
# """)
#                     if solution_dir and os.path.exists(solution_dir):
#                         f.write("COPY solution/ /home/coder/project/workspace/\n")

#                     f.write("""
# # Ports and working directory
# EXPOSE 3000 8080 8081
# WORKDIR /home/coder/project/workspace
# # ENV SHELL /bin/bash
# # ENTRYPOINT ["dumb-init", "fixuid", "-q", "/usr/bin/code-server", "--auth", "none", "--disable-file-downloads", "--disable-file-uploads", "--bind-addr", "0.0.0.0:3000", "/home/coder/project/workspace"]
# """)

            if self.language == "java":
                print("[DockerBuilderAgent] Using full Java + NVM + Node.js Docker setup...")
                with open(dockerfile_path, "w") as f:
#                     f.write(f"""
# # ===== JAVA + MAVEN + NODE (via NVM) =====
# FROM openjdk:17-slim

# # Base system setup
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#       curl \
#       bash \
#       git \
#       unzip \
#       chromium \
#       maven \
#       default-mysql-client \
#       ca-certificates \
#       apt-transport-https && \
#     rm -rf /var/lib/apt/lists/*
                            
# # ===== Install MySQL server =====
# RUN apt-get update && \
#     apt-get install -y wget lsb-release gnupg && \
#     wget https://dev.mysql.com/get/mysql-apt-config_0.8.29-1_all.deb && \
#     DEBIAN_FRONTEND=noninteractive dpkg -i mysql-apt-config_0.8.29-1_all.deb && \
#     apt-get update && \
#     DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server && \
#     mkdir -p /var/run/mysqld && \
#     chown -R mysql:mysql /var/run/mysqld && \
#     sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf && \
#     service mysql start || true && \
#     sleep 5 && \
#     mysql -e "CREATE DATABASE IF NOT EXISTS appdb;" || true && \
#     mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'examly'; FLUSH PRIVILEGES;" || true

# # NVM environment
# ENV NVM_DIR=/usr/local/nvm
# ENV NODE_VERSION=18.20.4
# ENV PATH=$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

# # Install NVM + Node.js
# RUN mkdir -p $NVM_DIR && \
#     curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh -o /tmp/install_nvm.sh && \
#     bash /tmp/install_nvm.sh && \
#     bash -lc "export NVM_DIR=$NVM_DIR && . $NVM_DIR/nvm.sh && \
#       nvm install $NODE_VERSION && \
#       nvm alias default $NODE_VERSION && \
#       nvm use default" && \
#     ln -sf $NVM_DIR/versions/node/v$NODE_VERSION/bin/node /usr/local/bin/node && \
#     ln -sf $NVM_DIR/versions/node/v$NODE_VERSION/bin/npm /usr/local/bin/npm && \
#     ln -sf $NVM_DIR/versions/node/v$NODE_VERSION/bin/npx /usr/local/bin/npx

# # Verify installations
# RUN java -version && mvn -version && node -v && npm -v && chromium --version

# # ===== Workspace setup =====
# WORKDIR /home/coder/project/workspace
# COPY {boilerplate_name} /home/coder/project/workspace/{boilerplate_name}

# # Extract boilerplate
# RUN unzip {boilerplate_name} -d /home/coder/project/workspace/boilerplate && \
#     if [ -d /home/coder/project/workspace/boilerplate/servicerequestscaffolding ]; then \
#       mv /home/coder/project/workspace/boilerplate/servicerequestscaffolding/* /home/coder/project/workspace/ || true; \
#     fi && \
#     for d in /home/coder/project/workspace/boilerplate/*; do \
#       if [ -d "$d" ]; then \
#         mv "$d" /home/coder/project/workspace/ || true; \
#       fi; \
#     done


# # Copy AI-generated solution (optional)
# """)
                    
                    f.write(f"""
# ===== JAVA + MAVEN + NODE (via NVM) + MARIADB =====
FROM openjdk:17-slim

# Base system setup
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      bash \
      git \
      unzip \
      chromium \
      maven \
      mariadb-server \
      ca-certificates \
      apt-transport-https && \
    rm -rf /var/lib/apt/lists/*

# === NVM setup ===
ENV NVM_DIR=/usr/local/nvm
ENV NODE_VERSION=18.20.4
ENV NODE_VERSION_14=14.17.1
ENV PATH=$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH
ENV PATH=$NVM_DIR/versions/node/v$NODE_VERSION_14/bin:$PATH
# === Install NVM + Node.js ===
                            
RUN mkdir -p $NVM_DIR && \
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh -o /tmp/install_nvm.sh && \
    bash /tmp/install_nvm.sh && \
    bash -lc "export NVM_DIR=$NVM_DIR && . $NVM_DIR/nvm.sh && \
      nvm install $NODE_VERSION && \
      nvm install $NODE_VERSION_14 && \
      nvm alias default $NODE_VERSION_14 && \
      nvm use default" && \
    ln -sf $NVM_DIR/versions/node/v$NODE_VERSION/bin/node /usr/local/bin/node && \
    ln -sf $NVM_DIR/versions/node/v$NODE_VERSION/bin/npm /usr/local/bin/npm && \
    ln -sf $NVM_DIR/versions/node/v$NODE_VERSION/bin/npx /usr/local/bin/npx && \
    ln -sf $NVM_DIR/versions/node/v$NODE_VERSION_14/bin/node /usr/local/bin/node14 && \
    ln -sf $NVM_DIR/versions/node/v$NODE_VERSION_14/bin/npm /usr/local/bin/npm14 && \
    ln -sf $NVM_DIR/versions/node/v$NODE_VERSION_14/bin/npx /usr/local/bin/npx14

# === Verify installations ===
RUN java -version && mvn -version && node -v && npm -v && chromium --version && mysqld --version

# === Workspace setup ===
WORKDIR /home/coder/project/workspace
COPY . /home/coder/project/workspace

# === MariaDB initial configuration ===
RUN mkdir -p /run/mysqld && \
    chown -R mysql:mysql /run/mysqld && \
    sed -i 's/^bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf && \
    service mariadb start && \
    sleep 5 && \
    mysql -e "CREATE DATABASE IF NOT EXISTS appdb;" && \
    mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'examly'; FLUSH PRIVILEGES;" || true

# === Environment variables for Spring Boot ===
ENV SPRING_DATASOURCE_URL=jdbc:mysql://localhost/appdb?createDatabaseIfNotExist=true
ENV SPRING_DATASOURCE_USERNAME=root
ENV SPRING_DATASOURCE_PASSWORD=examly

# === Expose common ports ===
EXPOSE 8080 3306

# === Start both MariaDB and Spring Boot ===
CMD service mariadb start && sleep 5 && mvn spring-boot:run
""")
                    if solution_dir and os.path.exists(solution_dir):
                        f.write("COPY solution/ /home/coder/project/workspace/\n")

                    f.write("""
# ===== Final configuration =====
ENV CHROME_BIN=/usr/bin/chromium
EXPOSE 3000 8080 8081
WORKDIR /home/coder/project/workspace
# Start MySQL when container runs
CMD service mysql start && tail -f /dev/null

# # ENV SHELL /bin/bash
# ENTRYPOINT ["dumb-init", "fixuid", "-q", "/usr/bin/code-server", "--auth", "none", "--disable-file-downloads", "--disable-file-uploads", "--bind-addr", "0.0.0.0:3000", "/home/coder/project/workspace"]

""")


            else:
                # ===== Existing .NET Docker setup =====
                with open(dockerfile_path, "w") as f:
                    f.write(f"""
FROM {self.base_images["dotnet"]}
RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*
WORKDIR /home/coder/project/workspace
COPY {boilerplate_name} /home/coder/project/workspace/{boilerplate_name}
RUN unzip {boilerplate_name} -d /home/coder/project/workspace/boilerplate
RUN for d in /home/coder/project/workspace/boilerplate/*; do \\
      if [ -d "$d" ]; then \\
        mv "$d" /home/coder/project/workspace/ || true; \\
      fi; \\
    done
""")
                    if solution_dir and os.path.exists(solution_dir):
                        f.write("COPY solution/ /home/coder/project/workspace/\n")
                    f.write("WORKDIR /home/coder/project/workspace/\n")

            # Copy AI-generated solution folder into temp_dir for Docker context
            if solution_dir and os.path.exists(solution_dir):
                print(f"[DockerBuilderAgent] Copying AI solution from {solution_dir} to Docker context...")
                target_solution = os.path.join(temp_dir, "solution")
                shutil.copytree(solution_dir, target_solution)

            print(f"[DockerBuilderAgent] Building image {image_tag} ...")
            image, logs = self.client.images.build(path=temp_dir, tag=image_tag, rm=True)
            print(f"[DockerBuilderAgent] ✅ Successfully built image: {image_tag}")
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
