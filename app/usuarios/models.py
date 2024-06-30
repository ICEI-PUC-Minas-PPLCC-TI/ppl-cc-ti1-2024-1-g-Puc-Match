from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,                                                                                                                                                                                                                                                                                                                                                                      
    Permission
)
from datetime import date
from django.utils import timezone
from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


# Create your models here.
class AccountManager(BaseUserManager):
    def create_user(    
        self,
        email,
        nome,
        cpf,   
        data_de_nascimento,
        matricula,
        curso,  # add this
        password=None,
        cep=None,  
        cidade=None,
        estado=None,  
        bairro=None,  
        rua=None,
    ):
        # User management
        if not email:
            raise ValueError("Email Obrigatorio.")
        if not nome:                                                                                                                                                                     
            raise ValueError("Nome Obrigatorio.")
        if not data_de_nascimento:
            raise ValueError("Data de Nascimento Obrigatoria.")
        if not matricula:
            raise ValueError("Matricula Obrigatoria.")
        if not curso:  # add this
            raise ValueError("Curso Obrigatorio.")

        # User object creation
        user = self.model(
            email=self.normalize_email(email),
            nome=nome,
            password=password,
            data_de_nascimento=data_de_nascimento,
            cep=cep,
            cidade=cidade,
            estado=estado,
            bairro=bairro,
            rua=rua,
            cpf=cpf,
            matricula=matricula,
            curso=curso,  # add this
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, nome, cpf, matricula, curso, data_de_nascimento, password):
        user = self.create_user(
            email=email,
            nome=nome,
            cpf=cpf,
            data_de_nascimento=data_de_nascimento,
            matricula=matricula,
            curso=curso,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    

class Usuarios(AbstractBaseUser, PermissionsMixin):

    groups = models.ManyToManyField(
            Group,
            verbose_name=('groups'),
            blank=True,
            help_text=(
                'The groups thisMatriculas user belongs to. A user will get all permissions '
                'granted to each of their groups.'
            ),
            related_name="usuarios_groups",
            related_query_name="user",
        )
    user_permissions = models.ManyToManyField(
            Permission,
            verbose_name=('user permissions'),
            blank=True,
            help_text=('Specific permissions for this user.'),
            related_name="usuarios_user_permissions",
            related_query_name="user",
        )
    email = models.EmailField(max_length=100, unique=True) # Campo Email
    nome = models.CharField(max_length=50)  # Campo Nome
    cpf = models.CharField(max_length=16, unique=True)  # Campo CPF
    matricula = models.IntegerField(unique=True)
    cep = models.CharField(max_length=9, blank=True, null=True)  # Campo CEP
    estado = models.CharField(max_length=50, blank=True, null=True)  # Campo Estado
    cidade = models.CharField(max_length=50, blank=True, null=True)  # Campo Cidade
    bairro = models.CharField(max_length=50, blank=True, null=True)  # Campo Bairro
    rua = models.CharField(max_length=50, blank=True, null=True)  # Campo Rua
    curso = models.CharField(max_length=50)  # Campo Curso
    data_de_nascimento = models.DateField(blank=False, null=True)  # Campo Data de Nascimento
    data_criacao = models.DateTimeField(auto_now_add=True)  # Campo Data de Criação
    password = models.CharField(max_length=50)  # Campo Senha
    
    
    # Tags
    is_verified = models.BooleanField(default=False)  # Campo Verificado

    # Permissions
    is_admin = models.BooleanField(default=False, verbose_name="admin")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


        
    # Sent object to AccountManager to create user
    objects = AccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "cpf", "matricula", "curso", "data_de_nascimento"]
    fields = ["id","email", "nome", "cpf", "matricula", "curso", "data_de_nascimento"]

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label: str) -> bool:
        return True

    def esconde_cpf(self):
        return "*" * 3 + "." + "*" * 3 + self.cpf[-6:-2] + self.cpf[-2] + self.cpf[-1]

    def retorna_idade(self):
        return (
            date.today().year
            - self.data_nascimento.year
            - (
                (date.today().month, date.today().day)
                < (self.data_nascimento.month, self.data_nascimento.day)
            )
        )
    
class Perfil(models.Model):     
    usuario = models.OneToOneField(Usuarios, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='media/', blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    SEXUALIDADE_CHOICES = [
        ('M', 'masculino'),
        ('F', 'feminino'),
        ('A', 'ambos'),
        ('N', 'nada')
    ]
    sexualidade = models.CharField(max_length=1, choices=SEXUALIDADE_CHOICES, default='N')
    data_de_nascimento = models.DateField(blank=False, null=True)

    def idade(self):
        if self.data_de_nascimento:
            hoje = date.today()
            nascimento = self.data_de_nascimento
            idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
            return idade
        else:
            return None
        
    def foto_url_modificado(self):
        if self.foto:
            return f"/usuarios{self.foto.url}"
        return None
        
    def __str__(self):
        return f'Perfil de {self.usuario.nome}'
    
    
@receiver(post_save, sender=User)
def criar_ou_atualizar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        # Ensure the User instance exists in the database.
        user = Usuarios.objects.filter(pk=instance.pk).first()
        if user:
            Perfil.objects.create(usuario=user)
        else:
            # Handle the case where the User instance does not exist.
            # This could involve logging an error or taking corrective action.
            pass
    else:
        # For updating, ensure the Perfil instance is linked to an existing User.
        if hasattr(instance, 'perfil'):
            instance.perfil.save()
        else:
            # Handle cases where the Perfil does not exist for the User.
            # This could involve creating a new Perfil or logging an error.
            pass

class Like(models.Model):
        
    usuario_que_deu_like = models.ForeignKey(Usuarios, related_name='likes_dados', on_delete=models.CASCADE)
    usuario_que_recebeu_like = models.ForeignKey(Usuarios, related_name='likes_recebidos', on_delete=models.CASCADE)
    data_like = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('usuario_que_deu_like', 'usuario_que_recebeu_like')

def verificar_match(usuario1, usuario2):
    # Verifica se ambos os usuários deram "like" um no outro
    match_usuario1_para_usuario2 = Like.objects.filter(usuario_que_deu_like=usuario1, usuario_que_recebeu_like=usuario2).exists()
    match_usuario2_para_usuario1 = Like.objects.filter(usuario_que_deu_like=usuario2, usuario_que_recebeu_like=usuario1).exists()

    return match_usuario1_para_usuario2 and match_usuario2_para_usuario1

def obter_usuarios_para_apresentacao(usuario):
    # Primeiro, encontre todos os usuários que deram "like" no usuário atual e que o usuário atual também deu "like"
    matches = Usuarios.objects.filter(
        likes_recebidos__usuario_que_deu_like=usuario,
        likes_dados__usuario_que_recebeu_like=usuario
    ).distinct()

    # Em seguida, encontre outros usuários, excluindo os matches já encontrados
    outros_usuarios = Usuarios.objects.exclude(id=usuario.id).exclude(id__in=matches).order_by('?')  # Ordena aleatoriamente

    # Combina os dois querysets, priorizando matches
    usuarios_para_apresentacao = list(matches) + list(outros_usuarios)

    return usuarios_para_apresentacao