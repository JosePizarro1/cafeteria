from django.contrib import admin
from .models import Sede, Producto, ProductoSede, Venta, DetalleVenta, Kardex,Cliente,Rol
class RolAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'es_admin', 'es_usuario', 'sede']  # Muestra estos campos en la lista
    list_filter = ['es_admin', 'es_usuario', 'sede']  # Filtros en la barra lateral
    search_fields = ['usuario__username', 'sede__nombre']  # Bè´‚squeda por nombre de usuario y sede
    fields = ['usuario', 'es_admin', 'es_usuario', 'sede']  # Campos que se mostrarè´°n en el formulario de ediciè´—n
    ordering = ['usuario']  # Ordena los registros por nombre de usuario

    def save_model(self, request, obj, form, change):
        """Sobrescribe el metodo save para asegurar reglas en roles."""
        # Asegura que al menos un campo de rol este marcado
        if not obj.es_admin and not obj.es_usuario:
            raise ValueError("El usuario debe tener al menos un rol asignado (Admin o Usuario).")
        super().save_model(request, obj, form, change)

admin.site.register(Rol, RolAdmin)

@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion', 'descripcion')
    search_fields = ('nombre', 'direccion')
    list_filter = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio_compra', 'precio_venta', 'cantidad_stock')
    search_fields = ('nombre',)
    list_filter = ('precio_venta',)


@admin.register(ProductoSede)
class ProductoSedeAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'sede', 'cantidad_stock')
    search_fields = ('producto__nombre', 'sede__nombre')
    list_filter = ('sede',)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'sede', 'cliente', 'fecha', 'metodo_pago', 'total', 'cancelada')  # A√±adido cancelada
    search_fields = ('sede__nombre', 'cliente__nombre', 'fecha')
    list_filter = ('sede', 'metodo_pago', 'cliente', 'cancelada')  # A√±adido cancelada al filtro
    date_hierarchy = 'fecha'

    def cliente(self, obj):
        return obj.cliente.nombre if obj.cliente else "Sin cliente"
    cliente.short_description = 'Cliente'



@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('producto__nombre', 'venta__sede__nombre')
    list_filter = ('producto',)


@admin.register(Kardex)
class KardexAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'sede', 'fecha', 'movimiento', 'cantidad', 'observacion')
    search_fields = ('producto__nombre', 'sede__nombre', 'observacion')
    list_filter = ('movimiento', 'fecha', 'sede')
    date_hierarchy = 'fecha'
    
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'telefono')
    search_fields = ('nombre', 'telefono')
    
    
