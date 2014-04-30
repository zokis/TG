# coding: utf-8
import json

from os.path import join
from random import choice, randint
from unicodedata import normalize

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers.json import DjangoJSONEncoder

VOGAIS = '!&0134@AEIOUYaeiouy'
CONSOANTES = '256789BCDFGHJKLMNPQRSTVWXZ_bcdfghjklmnpqrstvwxz'


def gera_password(min_len=14, max_len=19):
    c = lambda x: x % 2 == 0 and choice(CONSOANTES) or choice(VOGAIS)
    if min_len == max_len:
        length = min_len
    else:
        length = randint(min_len, max_len)
    return ''.join(c(i) for i in range(length))


def get_paginator_context(objects, request, n_pages=10):
    paginator = Paginator(objects, n_pages)
    page = request.GET.get('page')
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)
    return {
        'object_list': object_list, 'is_paginated': paginator.num_pages > 1, 'page_obj': object_list,
        'paginator': paginator
    }


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
