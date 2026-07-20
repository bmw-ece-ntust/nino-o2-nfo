FROM alpine:3.20 AS builder
RUN apk add --no-cache python3 py3-pip gcc libc-dev curl tar
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM alpine:3.20
RUN apk add --no-cache python3 curl git
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=nfo_microservice.settings
# Install Helm
ENV HELM_VERSION=v3.16.4
RUN curl -fsSL -o /tmp/helm.tar.gz https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz \
    && tar -zxf /tmp/helm.tar.gz -C /tmp \
    && mv /tmp/linux-amd64/helm /usr/local/bin/helm \
    && rm -rf /tmp/helm.tar.gz /tmp/linux-amd64
WORKDIR /app
COPY . /app/
EXPOSE 8000
CMD ["gunicorn", "nfo_microservice.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
