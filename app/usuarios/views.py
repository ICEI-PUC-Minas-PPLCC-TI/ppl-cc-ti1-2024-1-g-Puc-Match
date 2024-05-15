from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Usuarios, Matricula

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
        matricula_id = request.POST.get('matricula')
        curso = request.POST.get('curso')
        data_de_nascimento = request.POST.get('data_de_nascimento')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            return render(request, 'signup-page.html', {'error': 'As senhas não são iguais.'})
        matricula_id = request.POST['matricula']  # get matricula id from the request
        matricula, created = Matricula.objects.get_or_create(matricula=matricula_id)

        if not created:
            return render(request, 'signup-page.html', {'error': 'Matricula already exists.'})
        newUser = Usuarios.objects.create_user(
            email=email, 
            password=senha, 
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