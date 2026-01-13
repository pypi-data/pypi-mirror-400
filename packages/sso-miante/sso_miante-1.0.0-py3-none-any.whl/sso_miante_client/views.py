from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
from django.http import HttpResponseRedirect


def sso_login(request):
    url_api = settings.SSO_MIANTE_URL

    if request.method == 'POST':
        sso_id = settings.SSO_MIANTE_ID
        sso_secrets = settings.SSO_MIANTE_SECRETS
        username = request.POST.get('username')
        password = request.POST.get('password')

        body = {
            'sso_id': sso_id,
            'sso_secrets': sso_secrets,
            'username': username,
            'password': password,
            'server': str(request.get_host()),
        }

        response = requests.post(url_api, json=body)

        if response.status_code == 200:
            sso_info = response.json()
            status = sso_info.get('status')
            
            if status == 200:
                user = get_user_model().objects.filter(username=username)       
                if user.exists(): 
                    user = user.first() 
                else:
                    print('::::: CRIANDO USUÁRIO SSO ::::')
                    user = get_user_model()(username=username)
                    user.set_password(password)

                user.first_name = sso_info.get('first_name', '')
                user.last_name = sso_info.get('last_name', '')
                user.email = sso_info.get('email', '')

                user.save()
                login(request, user)
                return HttpResponseRedirect('/')

            elif status == 203:
                msg = sso_info.get('mensagem', 'ERRO ao Realizar o Login')
                raise Exception(msg)

    return render(request, 'sso-miante/login.html')


@login_required(login_url='sso_login')
def sso_logout(request):
    logout(request)
    return redirect('sso_login')

