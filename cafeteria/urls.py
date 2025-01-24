
from django.contrib import admin
from django.urls import path
from menu.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', login, name='login'),
    path('home/', home, name='home'),
    path('admin/', admin.site.urls),
    path('dashboard/', dashboard, name='dashboard'),
    path('productos/', productos_list, name='productos_list'),
    path('sedes/', sedes_list, name='sedes_list'),
    path('sedes/create/', sedes_create, name='sedes_create'),
    path('ventas/', ventas_list, name='ventas_list'),
    path('ventas/create/', ventas_create, name='ventas_create'),
    path('kardex/', kardex_list, name='kardex_list'),
    path('reportes/', reportes, name='reportes'),
]
