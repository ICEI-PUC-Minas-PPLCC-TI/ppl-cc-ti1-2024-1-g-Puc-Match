from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,                                                                                                                                                                                                                                                                                                                                                                      
    Permission
)
from datetime import datetime, date
from django.utils import timezone
# Create your models here.
class AccountManager(BaseUserManager):
    def create_user(    
        self,
        email,
        nome,
        cpf,
        data_nascimento,
        data_criacao,
        password=None,
    ):
        # User managemnt
        if not email:
            raise ValueError("Email Obrigatorio.")
        if not nome:                                                                                                                                                                     
            raise ValueError("Nome Obrigatorio.")
        if not data_nascimento:
            raise ValueError("Data de Nascimento Obrigatoria.")

       # User object creation
        user = self.model(
            email=self.normalize_email(email),
            nome=nome,
            password=password,
            data_nascimento=data_nascimento,
            data_criacao=data_criacao,
            cpf=cpf,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, nome, cpf, data_nascimento, data_criacao, password):
        user = self.create_user(
            email,
            nome,
            cpf,
            data_nascimento,
            data_criacao,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
class Matricula(models.Model):
    matricula = models.CharField(max_length=9, unique=True)

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
    id = models.AutoField(primary_key=True)  # Campo ID
    email = models.EmailField(max_length=100, unique=True) # Campo Email
    nome = models.CharField(max_length=50)  # Campo Nome
    cpf = models.CharField(max_length=16, unique=True)  # Campo CPF
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)  # Campo Matricula
    curso = models.CharField(max_length=50)  # Campo Curso
    data_de_nascimento = models.DateField(blank=False, null=True)  # Campo Data de Nascimento
    data_criacao = models.DateTimeField(auto_now_add=True)  # Campo Data de Criação

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
    REQUIRED_FIELDS = ["nome", "cpf", "matricula", "curso" ,"data_nascimento"]

    def __str__(self):
        return f"{self.nome}"

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
    