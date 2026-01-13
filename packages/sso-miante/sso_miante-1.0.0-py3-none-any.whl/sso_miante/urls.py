from django.urls import path
from . import views


urlpatterns = [
    path("sso/", views.sso_admin, name="sso_admin"),
    path("sso/<int:pk>/", views.sso_detail, name="sso_detail"),
    path("sso/<int:pk>/ativar-desativar/", views.sso_ativar_desativar, name="sso_ativar_desativar"),
    path("sso/status/", views.sso_status, name="sso_status"),
    path("sso/userinfo/", views.sso_userinfo, name="sso_userinfo"),
]
