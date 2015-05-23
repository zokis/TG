# coding: utf-8
import os
import sys

from ConfigParser import ConfigParser

from fabric.contrib import django
from tasks_manager.tasks import *
from tasks_manager.generic_fabfile import generic_fabfile

from django.conf import settings

# Abre o Arquivo settings.ini com o ConfigParser
ini = ConfigParser()
ini.readfp(open('settings.ini'))

# Lê o nome do projeto
PROJECT_NAME = ini.get('DEPLOY', 'project_name')
try:
    PROJECT_DIR = ini.get('DEPLOY', 'project_dir')
except:
    PROJECT_DIR = False

# Lê qual settings usar na produção
PROD_SETTINGS = ini.get('APP', 'settings_file')

sys.path.append(join('..', PROJECT_NAME))


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
django.settings_module(PROD_SETTINGS)


@task
def mapa_cidadao():
    # chama o fabfile genérico
    # reescrever aqui caso seja necessário
    generic_fabfile(env, settings, ini, PROJECT_NAME, PROJECT_DIR, PROD_SETTINGS)()