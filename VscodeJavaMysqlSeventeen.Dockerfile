# gcr.io/examly-dev/vscodejavamysqlseventeen
FROM codercom/code-server:4.20.0
RUN lsb_release -a
RUN sudo apt-get update && \
    sudo apt-get --no-install-recommends install -y software-properties-common && \
    sudo apt-get clean
RUN mkdir -p /home/coder/project && sudo chown -R 1000:1000 /home/coder/project
RUN sudo apt-get update && \
  sudo apt-get --no-install-recommends -yq install default-mysql-client maven && sudo apt-get clean
COPY ../common/config.yaml /home/coder/.config/code-server/
COPY ../common/.gitignore /home/coder/.gitignore
RUN git config --global core.excludesFile '~/.gitignore'
EXPOSE 3000 8081 8080
ENV PORT 3000
USER root
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
RUN sudo apt-get update && \
    sudo apt-get --no-install-recommends install -y openjdk-17-jdk && \
    sudo apt-get clean
RUN sudo echo "coder:neouser@123" | chpasswd
RUN sudo usermod -aG sudo coder
RUN sudo rm /etc/sudoers.d/nopasswd

# Install software packages
# nvm environment variables
ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION_12 12.22.1
ENV NODE_VERSION_14 14.17.1
ENV NODE_VERSION_16 16.4.0
ENV NODE_VERSION_18 18.20.4
ENV NODE_VERSION_20 20.9.0

# install nvm
# https://github.com/creationix/nvm#install-script
RUN curl --silent -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.2/install.sh | bash

# install node and npm
RUN source "$NVM_DIR"/nvm.sh \
    && nvm install "$NODE_VERSION_12" \
    && nvm install "$NODE_VERSION_14" \
    && nvm install "$NODE_VERSION_16" \
    && nvm install "$NODE_VERSION_18" \
    && nvm install "$NODE_VERSION_20" \
    && nvm alias default "$NODE_VERSION_14" \
    && nvm use default

# add node and npm to path so the commands are available
ENV NODE_PATH $NVM_DIR/v$NODE_VERSION_14/lib/node_modules
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION_14/bin:$PATH

# confirm installation
RUN node -v
RUN npm -v
ADD ../common/package.json  /
# RUN cd / && npm install --ignore-scripts
WORKDIR /
RUN npm install --ignore-scripts

RUN apt-get install chromium -y
ENV CHROME_BIN=/usr/bin/chromium
RUN echo "export CHROME_BIN=/usr/bin/chromium" >> /home/coder/.bashrc

USER coder
RUN code-server --install-extension vscjava.vscode-spring-initializr
RUN code-server --install-extension Angular.ng-template
RUN code-server --install-extension cweijan.vscode-mysql-client2
RUN code-server --install-extension dsznajder.es7-react-js-snippets
RUN code-server --install-extension johnpapa.angular2
RUN code-server --install-extension pivotal.vscode-boot-dev-pack
RUN code-server --install-extension redhat.java
RUN code-server --install-extension sonarsource.sonarlint-vscode
RUN code-server --install-extension visualstudioexptteam.vscodeintellicode
RUN code-server --install-extension vscjava.vscode-java-debug
RUN code-server --install-extension vscjava.vscode-java-dependency
RUN code-server --install-extension vscjava.vscode-maven
RUN code-server --install-extension vscjava.vscode-java-pack
RUN code-server --install-extension vscjava.vscode-java-test
RUN code-server --install-extension rangav.vscode-thunder-client

# Injecting js file
COPY ./modification/* /usr/lib/code-server/lib/vscode/out/vs/code/browser/workbench/

WORKDIR /home/coder/project/workspace 
ENV PATH /node_modules/karma-cli/bin:$PATH
ENV SHELL /bin/bash
RUN echo "source $NVM_DIR/nvm.sh" >> ~/.bashrc 
ENTRYPOINT dumb-init fixuid -q /usr/bin/code-server --auth none --disable-file-downloads --disable-file-uploads --bind-addr 0.0.0.0:3000 /home/coder/project/workspace 
