# coding: utf-8
import ConfigParser
import os
import sys


from fabric.contrib import django
from tasks_manager.tasks import *

sys.path.append('../mapa_cidadao')

ini = ConfigParser.ConfigParser()
ini.readfp(open('settings.ini'))

PROD_SETTINGS = ini.get('APP', 'settings_file')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
django.settings_module(PROD_SETTINGS)

from django.conf import settings


env.SECRET_KEY = settings.SECRET_KEY


@task
def mapa_cidadao():
    env.repository_type = 'git'
    env.secret_key = settings.SECRET_KEY

    if 'branch' not in env:
        env.branch = 'master'
    #  name of your project - no spaces, no special chars
    env.project = ini.get('DEPLOY', 'project_name')
    #  hg repository of your project
    env.repository = ini.get('DEPLOY', 'repository')
    ##env.repository = '<URL REPO GIT/BIT - PASSADO POR LINHA DE COMANDO>'
    #  hosts to deploy your project, users must be sudoers
    env.hosts = ini.get('DEPLOY', 'deploy_hosts').split(',')
    ##env.hosts = < LISTA DE HOSTS - PASSADO POR LINHA DE COMANDO>
    # additional packages to be installed on the server
    env.additional_packages = [
        'git-core',
    ]
    #  system user, owner of the processes and code on your server
    #  the user and it's home dir will be created if not present
    env.django_user = 'django'
    # user group
    env.django_user_group = env.django_user

    env.django_project_settings = PROD_SETTINGS

    #############################
    # PATHS
    ##############################

    # the code of your project will be located here
    env.django_user_home = join('/opt', env.django_user)
    #  projects paths
    env.projects_path = join(env.django_user_home, 'projects')
    env.code_root = join(env.projects_path, env.project)

    # manage.py path - used to run manangment commands
    env.django_project_root = join(env.code_root, 'mapa_cidadao')

    # this is the server path for all projects static_files
    STATIC_DIR = join(env.django_user_home, 'static_files')

    # MEDIA
    env.django_media_path = settings.MEDIA_ROOT  # Cara do settings
    env.django_media_root = settings.STATIC_DIR  # env usada para setar nginx.
    env.django_media_url = settings.MEDIA_URL

    # MEDIA
    env.django_static_path = settings.STATIC_ROOT  # usado no nginx
    env.django_static_root = settings.STATIC_DIR
    env.django_static_url = settings.STATIC_URL

    #
    # SOUTH CHECK                           ##
    #
    env.south_used = settings.INSTALLED_APPS.count('south') != 0

    #
    # VIRTUAL ENV                           ##
    #
    env.virtenv = join(env.django_user_home, 'envs', env.project)
    #  some virtualenv options, must have at least one
    env.virtenv_options = ['no-site-packages', ]  # 'distribute' is default
    #  location of your pip requirements file
    # http://www.pip-installer.org/en/latest/requirements.html#the-requirements-file-format
    #  set it to None to not use
    # cadu mudou abaixo
    # DEPLOY_DIR=os.path.dirname(__file__)
    #env.requirements_file = join(DEPLOY_DIR, 'requirements.txt')
    env.requirements_file = join(env.code_root, 'requirements', 'production.txt')
    #  always ask user for confirmation when run any tasks
    env.ask_confirmation = False

    # START gunicorn settings ###
    #  be sure to not have anything running on that port
    env.gunicorn_bind = ini.get('DEPLOY', 'gunicorn_bind')
    env.rungunicorn_script = '%(django_user_home)s/scripts/rungunicorn_%(project)s.sh' % env
    env.gunicorn_workers = 1
    env.gunicorn_worker_class = "eventlet"
    env.gunicorn_loglevel = "info"
    # END gunicorn settings ###

    # START nginx settings ###
    # 'camargocorrea.znc.com.br'  # Only domain name, without 'www' or 'http://'
    env.nginx_server_name = " ".join(settings.ALLOWED_HOSTS)
    env.nginx_conf_file = '%(django_user_home)s/configs/nginx/%(project)s.conf' % env

    # Maximum accepted body size of client request, in MB
    env.nginx_client_max_body_size = 10
    env.nginx_htdocs = '%(django_user_home)s/htdocs' % env
    # will configure nginx with ssl on, your certificate must be installed
    # more info here: http://wiki.nginx.org/HttpSslModule
    env.nginx_https = False
    # END nginx settings ###

    # START supervisor settings ###
    # http://supervisord.org/configuration.html#program-x-section-settings
    # default: env.project
    env.supervisor_program_name = env.project
    env.supervisorctl = '/usr/bin/supervisorctl'  # supervisorctl script
    env.supervisor_autostart = 'true'  # true or false
    env.supervisor_autorestart = 'true'  # true or false
    env.supervisor_redirect_stderr = 'true'  # true or false
    env.supervisord_conf_file = '%(django_user_home)s/configs/supervisord/%(project)s.conf' % env
    # END supervisor settings ###
