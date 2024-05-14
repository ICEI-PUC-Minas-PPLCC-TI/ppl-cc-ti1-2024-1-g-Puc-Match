from django.contrib import admin
from .models import Matricula, Usuarios



class UsuariosAdmin(admin.ModelAdmin):
    list_display = ('id','email', 'nome', 'data_de_nascimento', 'data_criacao', 'is_admin')

class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('id', 'matricula')



# Register your models here.
admin.site.register(Matricula, MatriculaAdmin) # Registrando o model Matricula no admin
admin.site.register(Usuarios, UsuariosAdmin) # Registrando o model Usuarios no admin