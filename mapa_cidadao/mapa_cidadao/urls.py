# coding: utf-8
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib.auth.views import logout
from django.contrib import admin
from django.views.generic.base import TemplateView

urlpatterns = patterns(
    '',
    url(r'^', include('mapa_cidadao.core.urls')),

    url(r'', include('social_auth.urls')),
    url(r'^logout/$', logout, {"next_page": "/"}, name="logout"),

    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (
            r'^media/(?P<path>.*)$',
            'django.views.static.serve',
            {
                'document_root': settings.MEDIA_ROOT
            }
        ),
        (r'^404/$', TemplateView.as_view(template_name='404.html')),
    )
