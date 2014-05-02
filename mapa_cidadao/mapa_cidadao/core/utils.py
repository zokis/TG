# coding: utf-8
import json

from os.path import join
from unicodedata import normalize
from django.core.serializers.json import DjangoJSONEncoder


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
