FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/app

WORKDIR /app

RUN pip install --upgrade pip

COPY ./requirements.txt /app/requirements.txt
COPY ./.env /app/.env

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install uvicorn

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade heads && python -m uvicorn app.main:app --host 0.0.0.0"]




