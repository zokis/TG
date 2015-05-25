# coding: utf-8
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib.auth.views import logout
from django.contrib import admin

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
        )
    )
