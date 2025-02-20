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
    path('ventas/list/', ventas_list, name='ventas_list'),
    path('ventas/create/', ventas_create, name='ventas_create'),
    path('kardex/', kardex_list, name='kardex_list'),
    path('reportes/', reportes, name='reportes'),
    path('logout/', logout_view, name='logout'),
    path('productos/crear/',productos_create, name='productos_create'),
    path('obtener-cantidad-actual/', obtener_cantidad_actual, name='obtener_cantidad_actual'),
    path('transferir-productos/', transferir_productos, name='transferir_productos'),
    path('obtener-cantidad-disponible/', obtener_cantidad_disponible, name='obtener_cantidad_disponible'),
    path('registrar-entrada/', registrar_entrada, name='registrar_entrada'),
    path('ventas/', registrar_venta, name='registrar_venta'),
    path('api/productos_por_sede/', productos_por_sede, name='productos_por_sede'),
    path('productos/eliminar/<int:producto_id>/', eliminar_producto, name='eliminar_producto'),
    path('productos/editar/<int:producto_id>/', editar_producto, name='editar_producto'),
    path('crear-usuario/', crear_usuario, name='crear_usuario'),
   path('guardar-usuario/', guardar_usuario, name='guardar_usuario'),
    path('asignar-rol-sede/', asignar_rol_sede, name='asignar_rol_sede'),
    path('guardar-roles/', guardar_roles, name='guardar_roles'),
    path('obtener_usuario_info/', obtener_usuario_info, name='obtener_usuario_info'),
    path('crear-cliente/', crear_cliente, name='crear_cliente'),
    path('inventario/', inventario, name='inventario'),
    path('deudores/', lista_deudores, name='deudores'),
    path("ventas/detalle/<int:venta_id>/", detalle_venta, name="detalle_venta"),
    path("ventas/marcar_pagada/<int:venta_id>/", marcar_venta_pagada, name="marcar_venta_pagada"),
]

# Agrega esta línea para servir archivos estáticos y archivos multimedia
if settings.DEBUG:  # Solo en modo desarrollo
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
