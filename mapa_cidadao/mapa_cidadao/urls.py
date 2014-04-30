# coding: utf-8
from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView
from django.contrib.auth.views import logout


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='base.html')),
    url(r'^', include('mapa_cidadao.core.urls')),

    url(r'', include('social_auth.urls')),
    url(r'^logout/$', logout, {"next_page": "/"}, name="logout"),
)
