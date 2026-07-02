#!/bin/bash
# Iniciar la aplicación web principal de Flask con Gunicorn
echo "Iniciando servidor web de Flask con Gunicorn..."
python -m gunicorn app:app
