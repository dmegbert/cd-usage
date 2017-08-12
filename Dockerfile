FROM ubuntu:16.04

MAINTAINER David Egbert "dmegbert@us.ibm.com"

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

ADD /Users/davidegbert/shellScripts/vertica.sh vertica.sh
RUN vertica.sh

EXPOSE 5000
COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "controller.py" ]

#docker run --name flask_cd --rm -p 5000:5000 --env DB_HOST --env DB_USER --env DB_PORT --env DB_PASSWORD --env DB_NAME --env SECRET_KEY flask
#sudo docker run --name flask_cd --rm -p 5000:5000 --env-file vertica.list flask &>/dev/null &