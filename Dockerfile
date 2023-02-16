FROM mysql:8

EXPOSE 3306

COPY practice_user.sql /docker-entrypoint-initdb.d/practice_user.sql

FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN pip install mysql-connector-python

COPY practice_user.sql .

EXPOSE 8000

COPY . .

CMD python -m uvicorn user:app --reload
