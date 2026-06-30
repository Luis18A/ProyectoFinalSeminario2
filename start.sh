#!/bin/bash
# Iniciar el Celery worker en segundo plano para procesar tareas asíncronas de Scraping
echo "Iniciando Celery Worker..."
python -m celery -A backend.tasks.celery worker --loglevel=info &

# Iniciar la aplicación web principal de Flask con Gunicorn en primer plano
echo "Iniciando servidor web de Flask con Gunicorn..."
python -m gunicorn app:app
