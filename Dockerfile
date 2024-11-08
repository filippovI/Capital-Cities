FROM python:3.11.0rc2-slim-buster

WORKDIR /opt/app

ENV TZ 'UTC'
ENV PYTHONUNBUFFERED=1

RUN apt update \
    && apt install bash \
    && pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]