from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Usuarios, Perfil, Like
from django.core.files.storage import FileSystemStorage
from django.conf import settings 
from django.http import JsonResponse
from django.contrib import messages
import os
from django.db import IntegrityError

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
    usuario = request.user
    
    # Exclui os usuários que já receberam like ou dislike do usuário atual
    usuarios_excluidos = list(Like.objects.filter(usuario_que_deu_like=usuario).values_list('usuario_que_recebeu_like', flat=True))
    usuarios_excluidos.append(usuario.id)  # Adiciona o próprio usuário
    
    perfis = Perfil.objects.exclude(usuario=usuario).exclude(id__in=usuarios_excluidos)

    if request.method == 'POST':
        perfil_id = request.POST.get('perfilId')
        acao = request.POST.get('acao')  # 'like' ou 'dislike'

        if acao in ['like', 'dislike'] and perfil_id:
            try:
                usuario_que_recebeu_like = Usuarios.objects.get(id=perfil_id)
                
                # Cria um novo registro de like/dislike
                like = Like.objects.create(
                    usuario_que_deu_like=usuario, 
                    usuario_que_recebeu_like=usuario_que_recebeu_like,
                    # Remova acao, pois isso não é um campo do modelo Like
                )
                
                # Retorna uma mensagem de sucesso para requisições AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'message': f'{acao.capitalize()} registrado com sucesso'}, status=200)
                else:
                    # Redireciona ou retorna uma resposta apropriada para requisições normais (não AJAX)
                    return redirect('plataforma')
            
            except Usuarios.DoesNotExist:
                return JsonResponse({'error': 'Usuário não encontrado'}, status=404)
            except IntegrityError:
                return JsonResponse({'error': 'Ocorreu um erro ao processar seu like'}, status=400)

    # Lógica para obter usuários para apresentação
    likes_dados = Like.objects.filter(usuario_que_deu_like=usuario).values_list('usuario_que_recebeu_like', flat=True)
    likes_recebidos = Like.objects.filter(usuario_que_recebeu_like=usuario).values_list('usuario_que_deu_like', flat=True)

    matches_mutuos_ids = set(likes_dados).intersection(set(likes_recebidos))
    matches_mutuos = Usuarios.objects.filter(id__in=matches_mutuos_ids)
    outros_usuarios = Usuarios.objects.exclude(id=usuario.id).exclude(id__in=matches_mutuos_ids)

    usuarios_para_apresentacao = list(matches_mutuos) + list(outros_usuarios)
    
    # Verifica se a requisição é AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Retorna apenas os dados necessários em formato JSON para AJAX
        data = {
            'usuarios_para_apresentacao': [{'id': u.id, 'nome': u.nome} for u in usuarios_para_apresentacao],
            'perfis': list(perfis.values('id', 'descricao'))
        }
        return JsonResponse(data)
    else:
        # Renderiza o template HTML normalmente para requisições não AJAX
        return render(request, 'plataforma.html', {
            'usuarios_para_apresentacao': usuarios_para_apresentacao, 
            'perfis': perfis
        })



@login_required
def perfil(request):
    try:
        user_profile = request.user.perfil
    except Perfil.DoesNotExist:
        user_profile = Perfil.objects.create(usuario=request.user)

    # Synchronize birth date
    if user_profile.data_de_nascimento != request.user.data_de_nascimento:
        user_profile.data_de_nascimento = request.user.data_de_nascimento
        user_profile.save()

    # Prepare initial context
    context = {
        'nome': request.user.nome,
        'data_de_nascimento': request.user.perfil.data_de_nascimento,
        'descricao': user_profile.descricao if user_profile.descricao else '',
        'foto': user_profile.foto_url_modificado() if user_profile.foto else None,
        'sexo': user_profile.get_sexualidade_display() if user_profile.sexualidade else None,
    }

    if request.method == 'POST':
        descricao = request.POST.get('descricao')
        foto = request.FILES.get('foto')
        sexo = request.POST.get('sexo')

        user_profile.descricao = descricao
        user_profile.sexualidade = sexo  # Atualiza o campo sexualidade

        if foto:
            user_profile.foto = foto

        user_profile.save()

        # Update context with new or existing values
        context.update({
            'descricao': descricao,
            'foto': user_profile.foto.url if user_profile.foto else None,
            'sexo': user_profile.get_sexualidade_display() if user_profile.sexualidade else None,
        })

        return render(request, 'plataforma.html', context)  # Redireciona para evitar resubmissão do formulário

    return render(request, 'profile-page.html', context)