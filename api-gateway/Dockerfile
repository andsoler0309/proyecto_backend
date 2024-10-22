FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=postgresql+psycopg2://postgres:1234@192.168.0.10/usuarios
ENV GESTOR_CLIENTES_BASE_URL=https://gestor-clientes-649096178068.us-central1.run.app
ENV GENERACION_REPORTES_BASE_URL=https://generacion-reportes-649096178068.us-central1.run.app
ENV GESTOR_INCIDENTES_BASE_URL=https://gestor-incidentes-649096178068.us-central1.run.app
ENV GESTOR_AGENTES_BASE_URL=https://gestor-agentes-649096178068.us-central1.run.app
ENV SERVICIO_IA_BASE_URL=https://servicio-ia-649096178068.us-central1.run.app

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

COPY . .

EXPOSE 5000
ENV FLASK_APP=app.py
ENTRYPOINT [ "flask", "run", "--host=0.0.0.0"]