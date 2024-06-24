from django.contrib import admin
from .models import Usuarios, Perfil



class UsuariosAdmin(admin.ModelAdmin):
    list_display = ('id','email', 'nome', 'data_de_nascimento', 'data_criacao', 'is_admin')

class PerfisAdmin(admin.ModelAdmin):
    list_display = ('id','usuario',  'descricao', 'foto', 'data_de_nascimento')


# Register your models here.
admin.site.register(Usuarios, UsuariosAdmin) # Registrando o model Usuarios no admin
admin.site.register(Perfil, PerfisAdmin) # Registrando o model Usuarios no admin