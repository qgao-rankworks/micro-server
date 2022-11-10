FROM nginx/unit:1.26.1-python3.9

# set working directory

# RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app/api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc \
  && apt-get clean 


# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY config.json /docker-entrypoint.d/config.json

# add app
COPY . .

COPY api-start.sh /mnt/scripts/api-start.sh
RUN chmod 777 /mnt/scripts/api-start.sh


EXPOSE 80