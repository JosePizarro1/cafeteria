from django.db import models
from django.contrib.auth.models import User


class Sede(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.TextField()
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
class Rol(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="rol")  # Relación uno a uno con el usuario de Django
    es_admin = models.BooleanField(default=False)  # Check para saber si es admin
    es_usuario = models.BooleanField(default=False)  # Check para saber si es un usuario regular
    sede = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True, blank=True, related_name="usuarios")  # Relación con sede

    def __str__(self):
        rol = "Admin" if self.es_admin else "Usuario"
        return f"{self.usuario.username} ({rol}) - {self.sede.nombre if self.sede else 'Sin Sede'}"
        

class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_stock = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    def calcular_ganancia(self):
        return self.precio_venta - self.precio_compra


class ProductoSede(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)
    cantidad_stock = models.IntegerField(default=0)  # Stock específico para la sede

    def __str__(self):
        return f"{self.producto.nombre} en {self.sede.nombre}"

    def transferir_stock(self, cantidad, sede_destino):
        """Método para transferir stock entre sedes."""
        # Actualiza el stock en la sede origen
        self.cantidad_stock -= cantidad
        self.save()

        # Busca el stock del producto en la sede destino
        producto_sede_destino, creado = ProductoSede.objects.get_or_create(
            producto=self.producto, sede=sede_destino
        )

        # Actualiza el stock en la sede destino
        producto_sede_destino.cantidad_stock += cantidad
        producto_sede_destino.save()

class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=15, blank=True, null=True)  # Teléfono opcional

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    METODO_PAGO_CHOICES = [
        ('EF', 'Efectivo'),
        ('YP', 'Yape'),
        ('CR', 'Crédito'),
    ]

    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name="ventas")
    fecha = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=2, choices=METODO_PAGO_CHOICES, default='EF')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="ventas")  # Cliente opcional
    cancelada = models.BooleanField(default=False)  # Campo para ventas canceladas

    def __str__(self):
        return f"Venta {self.id} - {self.sede.nombre} ({self.fecha.strftime('%Y-%m-%d %H:%M')})"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="detalles_venta")
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        # Calcular subtotal antes de guardar
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        # Actualizar stock del producto en la sede
        producto_sede = ProductoSede.objects.get(producto=self.producto, sede=self.venta.sede)
        producto_sede.cantidad_stock -= self.cantidad
        producto_sede.save()


class Kardex(models.Model):
    MOVIMIENTO_CHOICES = [
        ('IN', 'Ingreso'),
        ('OUT', 'Salida'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="kardex")
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name="kardex", null=True, blank=True)  # ahora es opcional
    fecha = models.DateTimeField(auto_now_add=True)
    movimiento = models.CharField(max_length=3, choices=MOVIMIENTO_CHOICES)
    cantidad = models.IntegerField()
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Kardex {self.producto.nombre} - {self.movimiento} ({self.fecha.strftime('%Y-%m-%d')})"