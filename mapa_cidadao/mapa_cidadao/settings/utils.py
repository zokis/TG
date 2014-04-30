# coding: utf-8
from ConfigParser import ConfigParser

OPT_DJANGO_CONF_APP = '/opt/django/configs/apps/mapa_cidadao.conf'


def gen_get_config_or(config):
    def inner(section, option, default=None):
        try:
            return config.get(section, option)
        except:
            return default
    return inner


def read_config_file():
    '''
    tenta ler arquivo de configuração
    Return: objeto do tipo ConfigParser
    '''
    config = ConfigParser()
    config_file = None
    try:
        config_file = open(OPT_DJANGO_CONF_APP)
    except:
        return config

    config.readfp(config_file)

    return config
