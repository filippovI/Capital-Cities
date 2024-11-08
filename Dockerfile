FROM python:3.13.0b4-alpine3.19

WORKDIR /app

ENV TZ 'UTC'
ENV PYTHONUNBUFFERED=1

RUN sudo apk update \
    && sudo apk add bash \
    && sudo pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN sudo pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]