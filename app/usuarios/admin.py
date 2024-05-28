from django.contrib import admin
from .models import Usuarios



class UsuariosAdmin(admin.ModelAdmin):
    list_display = ('id','email', 'nome', 'data_de_nascimento', 'data_criacao', 'is_admin')


# Register your models here.
admin.site.register(Usuarios, UsuariosAdmin) # Registrando o model Usuarios no admin