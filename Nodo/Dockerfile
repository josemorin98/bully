FROM python:3.8-buster

#install requeriments
RUN useradd -ms /bin/bash admin
RUN pip install flask
RUN pip install requests
RUN pip install pandas
RUN python -m pip install --upgrade pip
RUN pip3 install queuelib

COPY ./ /app
WORKDIR  /app
EXPOSE 5000
