# coding: utf-8
from django.conf import settings
from datetime import date, timedelta


class KeepLoggedInMiddleware(object):
    def process_request(self, request):

        print request.user.is_authenticated(), 'is_authenticated'

        print dir(request.user)

        if not settings.KEEP_LOGGED_KEY in request.session or not request.user.is_authenticated():
            if request.method == 'POST':
                if settings.KEEP_LOGGED_KEY in request.POST:
                    request.session[settings.KEEP_LOGGED_KEY] = True
            return

        if request.session[settings.KEEP_LOGGED_KEY] != date.today():
            request.session.set_expiry(timedelta(days=settings.KEEP_LOGGED_DURATION))
            request.session[settings.KEEP_LOGGED_KEY] = date.today()
