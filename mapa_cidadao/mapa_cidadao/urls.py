# coding: utf-8
from django.conf.urls import include, patterns, url
from django.contrib.auth.views import logout

urlpatterns = patterns(
    '',
    url(r'^', include('mapa_cidadao.core.urls')),

    url(r'', include('social_auth.urls')),
    url(r'^logout/$', logout, {"next_page": "/"}, name="logout"),
)
