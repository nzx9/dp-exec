
FROM python:3.11.2-buster


RUN apt-get update
RUN apt-get install software-properties-common -y

RUN \
  apt-get update && \
  apt-get install -y openjdk-11-jdk && \
  rm -rf /var/lib/apt/lists/*

RUN mkdir build


WORKDIR /build


COPY . .


RUN pip install -r requirements.txt
# --no-cache-dir 

EXPOSE 8000


WORKDIR /build/app

# CMD gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 3600  --graceful-timeout 3600
CMD python -m uvicorn main:app --host 0.0.0.0 --port 8000