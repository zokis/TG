from django.contrib import admin
from django import forms
from .models import Categoria

from jsonfield.fields import JSONFormField


class CategoriaForm(forms.ModelForm):
    estilo = JSONFormField()

    class Meta:
        model = Categoria


class CategoriaAdmin(admin.ModelAdmin):
    form = CategoriaForm


admin.site.register(Categoria, CategoriaAdmin)
