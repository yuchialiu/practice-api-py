FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN pip install mysql-connector-python

COPY practice_user.sql .

EXPOSE 8000

COPY . .

RUN apt-get update && apt-get install -y default-mysql-client

ENV DB_HOST=localhost
ENV DB_PORT=3306
ENV DB_USERNAME=your-username
ENV DB_PASSWORD=your-password
ENV DB_DATABASE=practice

CMD mysql -h $DB_HOST -P $DB_PORT -u $DB_USERNAME -p$DB_PASSWORD $DB_DATABASE < practice_user.sql && uvicorn user:app --host 0.0.0.0 --port 8000

