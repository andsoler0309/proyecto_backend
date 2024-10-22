FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=postgresql+psycopg2://postgres:1234@192.168.0.10/usuarios
ENV GESTOR_INCIDENTES_BASE_URL=https://gestor-incidentes-649096178068.us-central1.run.app

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
ENV FLASK_APP=app.py
ENTRYPOINT [ "flask", "run", "--host=0.0.0.0"]