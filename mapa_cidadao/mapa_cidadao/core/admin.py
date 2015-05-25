from django.contrib import admin
from django import forms
from .models import Categoria


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        exclude = ['estilo']


class CategoriaAdmin(admin.ModelAdmin):
    form = CategoriaForm


admin.site.register(Categoria, CategoriaAdmin)
