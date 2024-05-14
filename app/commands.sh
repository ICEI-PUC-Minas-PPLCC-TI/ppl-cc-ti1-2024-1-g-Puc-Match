#!/bin/bash

# Ativa o ambiente virtual
source venv/bin/activate

# Navega até a pasta do projeto Django
cd ti-1-ppl-cc-m-20241-3-ti-1-ppl-cc-m-20241-3/app

# Instala todas dependências do projeto
pip install -r requirements.txt

# Executa as migrações
python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Inicia o servidor Django
python manage.py runserver 