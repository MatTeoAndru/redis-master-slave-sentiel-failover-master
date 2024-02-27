FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /flask-app

COPY requirements.txt /flask-app

COPY /flask-app /flask-app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

ENTRYPOINT ["python3"]

CMD ["app.py"]