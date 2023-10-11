FROM mason77804/monophonic:1-1
WORKDIR /
#Add the webserver git repo
RUN git clone https://github.com/MasonDill/mono-web.git
#Get the il conversion repo
RUN git clone https://github.com/MasonDill/semantic_to_mei.git
#Install pip for python3
RUN wget https://bootstrap.pypa.io/pip/3.5/get-pip.py
RUN python3 get-pip.py
#Install music21
RUN python3 -m pip install music21

#start the webserver
WORKDIR /mono-web
CMD ["python3", "app.py"]