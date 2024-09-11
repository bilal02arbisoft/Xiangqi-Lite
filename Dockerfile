
FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev


WORKDIR /app


COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


COPY . /app/

COPY ./entrypoint.sh /app/entrypoint.sh


RUN chmod +x /app/entrypoint.sh

EXPOSE 8000


ENTRYPOINT ["/app/entrypoint.sh"]
