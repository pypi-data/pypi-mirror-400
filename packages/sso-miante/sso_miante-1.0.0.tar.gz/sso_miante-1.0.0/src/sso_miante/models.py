from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout, get_user_model
import secrets
from secrets import token_urlsafe


class SsoMiante(models.Model):
    data_inclusao = models.DateField('Data Inclusão', auto_now_add=True)
    app = models.EmailField('APP', max_length=200, unique=True)
    app_id = models.EmailField('APP ID', max_length=200, unique=True)
    secrets = models.EmailField('Secrets', max_length=1000)
    server = models.TextField('server', max_length=5000, default='')
    ativo = models.BooleanField('active?', default=True)

    class Meta:
        db_table = 'sso_miante'
        verbose_name = "SSO Miante"
        verbose_name_plural = "SSO Miante"
        ordering = ['app']

    def __str__(self): return self.app
    
    def CREATE_HASHS(n=50):
        n_id = int(n/2)
        return secrets.token_urlsafe(n_id), secrets.token_urlsafe(n)
    
    def CREATE(id, secrets, app_name, app_server):
        secrets = make_password(secrets)
        sso = SsoMiante(app_id=id, secrets=secrets, app=app_name, server=app_server)
        sso.save()
        return sso

    def AUTHENTICATE(app_id, secrets, username, password, server):
        # Verifica a Autenticação do APP
        check = False
        sso = SsoMiante.objects.filter(app_id=app_id).first()
        if sso:            
            if not sso.ativo: raise Exception('APP SSO Inativo!!!')
            if server not in sso.server: raise Exception('Servidor não permitido!!!')
            check = check_password(secrets, sso.secrets)        
        if check is False: raise Exception('Erro na Autenticação do Aplicativo!!!')
        
        # Verifica a Autenticação do Usuário
        User = get_user_model()
        try:
            obj = User.objects.get(username=username)
            if not obj.is_active:
                raise Exception('Usuário INATIVO!!!')                
        except User.DoesNotExist:
            raise Exception('Usuário não encontrado!!!')
        
        if obj.check_password(password) is False: raise Exception('Senha Inválida!!!')
        
        sso_user = {'status': 200, 'id': obj.id, 'username': obj.username, 'first_name': obj.first_name, 'last_name': obj.last_name, 'email': obj.email}

        return sso_user

    