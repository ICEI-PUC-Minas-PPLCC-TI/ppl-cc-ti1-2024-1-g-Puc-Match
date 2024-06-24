from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Usuarios, Perfil
from django.core.files.storage import FileSystemStorage
from django.conf import settings 
import os
# Create your views here.

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('homepage:home')
        else:
            return render(request, 'login-page.html', {'error': 'Invalid login credentials.'})
    else:
        return render(request, 'login-page.html')

@login_required
def logout(request):
    auth_logout(request)
    return redirect('homepage:home')


def signup(request):
    if request.method == 'POST':
        usuario_email = Usuarios.objects.filter(email=request.POST['email']).first()
        usuario_nome = Usuarios.objects.filter(nome=request.POST['nome']).first()
        if usuario_email or usuario_nome:
            return render(request, 'signup-page.html', {'error': 'Já existe um usuário com o mesmo e-mail ou mesmo nome'})

        nome = request.POST.get('nome')
        email = request.POST.get('email')
        cpf = request.POST.get('cpf')
        cep = request.POST.get('cep')
        estado = request.POST.get('estado')
        cidade = request.POST.get('cidade')
        bairro = request.POST.get('bairro')
        rua = request.POST.get('rua')
        matricula = request.POST.get('matricula')
        curso = request.POST.get('curso')
        data_de_nascimento = request.POST.get('data_de_nascimento')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            return render(request, 'signup-page.html', {'error': 'As senhas não são iguais.'})
        
        if Usuarios.objects.filter(matricula=matricula).exists():
            return render(request, 'signup-page.html', {'error': 'Matricula already exists.'})

        newUser = Usuarios.objects.create_user(
            email=email, 
            password=senha,
            cep=cep,
            estado=estado,
            cidade=cidade,
            bairro=bairro,
            rua=rua, 
            nome=nome, 
            cpf=cpf, 
            matricula=matricula, 
            curso=curso, 
            data_de_nascimento=data_de_nascimento
        )
        newUser.save()
        return redirect('homepage:home')

    else: 
        return render(request, 'signup-page.html')

@login_required
def plataforma(request):
    return render(request, 'plataforma.html')

@login_required
def perfil(request):

    user_profile, created = Perfil.objects.get_or_create(usuario=request.user)
    context = {
        'nome': request.user.nome,
        'data_de_nascimento': request.user.data_de_nascimento,
        'descricao': user_profile.descricao if user_profile.descricao else '',
        'foto': user_profile.foto.url if user_profile.foto else None,
    }

    if request.method == 'POST':
        descricao = request.POST.get('descricao')
        foto = request.FILES.get('foto') if 'foto' in request.FILES else None
        user_profile.descricao = descricao

        if foto:
            _, ext = os.path.splitext(foto.name)
            sanitized_filename = os.path.basename(foto.name)
            novo_nome_arquivo = f"{request.user.nome}_foto_perfil{ext}"
            foto.name = novo_nome_arquivo
            user_profile.foto = foto
        user_profile.save()
        context.update({
            'descricao': descricao,
            'foto': user_profile.foto.url if user_profile.foto else None,
        })
    
    print(user_profile.foto.url)

    return render(request, 'profile-page.html', context)