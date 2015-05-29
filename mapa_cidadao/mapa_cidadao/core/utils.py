# coding: utf-8
import json

from os.path import join
from unicodedata import normalize
from django.conf import settings
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder

from municipios.models import Municipio

MUNICIPIO_ID = getattr(settings, 'MUNICIPIO_ID', 3549904)
MUNICIPIO = Municipio.objects.get(id_ibge=MUNICIPIO_ID)


def get_upload_path_docs(instance, filename):
    '''
    retorna arquivo na estrutura de diretórios:
    arquivos/
           |
           app1/
           |  |
           |  model_1/
           |  |     |
           |  |     arquivo1
           |  |     arquivo2
           |  |
           |  model_2/
           |        |
           |        arquivo3
           |
           app2/
              |
              model_3/
                    |
                    arquivo4

    '''
    content_type_app = normalize('NFKD', instance.content_type.app_label).replace(' ', '_')
    content_type_name = normalize('NFKD', instance.content_type.name).replace(' ', '_')
    filename = normalize('NFKD', filename).encode('ascii', 'ignore').replace(' ', '_')

    return join('arquivos', content_type_app, content_type_name, filename)


class JSONSerializer(object):
    def dumps(self, obj):
        return json.dumps(obj, separators=(',', ':'), cls=DjangoJSONEncoder).encode('latin-1')

    def loads(self, data):
        return json.loads(data.decode('latin-1'))


def is_last(objects):
    it = iter(objects)
    last = it.next()
    for val in it:
        yield last, False
        last = val
    yield last, True


def get_geom_from_cache():
    geom = cache.get("geom_%s" % MUNICIPIO_ID)
    if geom is None:
        geom = MUNICIPIO.geom
        geom.transform(900913)
        cache.set("geom_%s" % MUNICIPIO_ID, geom, 30*24*60*60)  # 1 mês
    return geom
