from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import json
from .models import SsoMiante

def sso_status(request):
    return HttpResponse("SSO Miante instalado e funcionando.")


def sso_admin(request):
    id, secrets = SsoMiante.CREATE_HASHS()
    if request.method == 'POST':
        nome = request.POST.get('nome_app')
        app_id = request.POST.get('app_id')
        app_secret = request.POST.get('app_secret')
        app_server = request.POST.get('app_server')
        SsoMiante.CREATE(app_id, app_secret, nome, app_server)

    apps = SsoMiante.objects.all()
    context = {'id_app': id, 'secrets': secrets, 'apps': apps}
    return render(request, 'sso/admin.html', context)


def sso_detail(request, pk):
    obj = get_object_or_404(SsoMiante, pk=pk)
    if request.method == 'POST':        
        app_server = request.POST.get('app_server', None)
        if app_server is not None:
            obj.server = app_server
            obj.save()
    
    context = {'obj': obj}
    return render(request, 'sso/detail.html', context)


def sso_ativar_desativar(request, pk):
    obj = SsoMiante.objects.get(pk=pk)
    if obj.ativo: obj.ativo = False
    else: obj.ativo = True
    obj.save()
    return redirect('sso_detail', pk=pk)


@csrf_exempt
def sso_userinfo(request):
    dados = {}
    try:
        if request.method == 'POST':
            dados_json = request.body.decode('utf-8')            
            dados = json.loads(dados_json)
            
            # Verificando Permissões
            sso_id      = dados.get('sso_id', '-')
            sso_secrets = dados.get('sso_secrets', '-')
            username    = dados.get('username', '-')
            password    = dados.get('password', '-')
            server    = dados.get('server', '-')

            dados = SsoMiante.AUTHENTICATE(sso_id, sso_secrets, username, password, server)

    except Exception as e:
        dados = {'status': 203, 'mensagem': f'ERRO: {e.args[0]}'}

    return HttpResponse(
        json.dumps(dados, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )

