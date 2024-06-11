#!/bin/bash
python -m venv venv

# Ativa o ambiente virtual
source venv/bin/activate


# Instala todas dependências do projeto
pip install -r requirements.txt

# Executa as migrações
python manage.py collectstatic --noinput --clear
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Inicia o servidor Django
python manage.py runserver