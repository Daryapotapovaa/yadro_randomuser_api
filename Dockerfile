FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "randomuser_project.wsgi"]