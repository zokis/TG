# coding: utf-8
from django.db import models


def custom_objects(Manager=models.Manager, QuerySet=models.query.QuerySet):
    def oe_inner(Mixin, Manager=models.Manager, QuerySet=models.query.QuerySet):
        class MixinManager(Manager, Mixin):
            class MixinQuerySet(QuerySet, Mixin):
                pass

            def get_query_set(self):
                return self.MixinQuerySet(self.model, using=self._db)

        return MixinManager()

    if issubclass(Manager, models.Manager):
        return lambda Mixin: oe_inner(Mixin, Manager, QuerySet)
    else:
        return oe_inner(Mixin=Manager)
