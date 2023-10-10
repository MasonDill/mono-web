FROM node:latest
WORKDIR /
RUN git clone https://gitea.dill.digital/mason/monophonic-webserver.git
WORKDIR /monophonic-webserver/
RUN npm install
CMD ["node", "monophonic_api.js"]