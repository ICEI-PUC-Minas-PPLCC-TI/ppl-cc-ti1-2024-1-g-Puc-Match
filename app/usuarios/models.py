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
from django.contrib import admin
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
    matricula = models.IntegerField(max_length=9, unique=True)
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