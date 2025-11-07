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
# # ENV SHELL /bin/bash
# # Start MySQL when container runs

# CMD service mysql start && tail -f /dev/null

# ENTRYPOINT ["dumb-init", "fixuid", "-q", "/usr/bin/code-server", "--auth", "none", "--disable-file-downloads", "--disable-file-uploads", "--bind-addr", "0.0.0.0:3000", "/home/coder/project/workspace"]
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
