FROM jupyter/base-notebook

USER root

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 git -y

RUN mkdir /app
ADD requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install --upgrade pip \
  && pip install -r requirements.txt



EXPOSE 8888

USER ${NB_UID}

WORKDIR "${HOME}"
