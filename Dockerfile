FROM python:3.13.0-alpine3.20

WORKDIR /project

ENV TZ 'UTC'
ENV PYTHONUNBUFFERED=1

RUN apk update \
    && apk install -y gcc bash \
    && pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH "${PYTHONPATH}:app"
ENTRYPOINT ["python", "main.py"]