from django.contrib import admin
from .models import Usuarios, Perfil, Like



class UsuariosAdmin(admin.ModelAdmin):
    list_display = ('id','email', 'nome', 'data_de_nascimento', 'data_criacao', 'is_admin')

class PerfisAdmin(admin.ModelAdmin):
    list_display = ('id','usuario',  'descricao', 'foto', 'sexualidade' ,'data_de_nascimento')

class LikesAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario_que_deu_like', 'usuario_que_recebeu_like','data_like')

# Register your models here.
admin.site.register(Usuarios, UsuariosAdmin) # Registrando o model Usuarios no admin
admin.site.register(Perfil, PerfisAdmin) # Registrando o model Usuarios no admin
admin.site.register(Like, LikesAdmin) # 