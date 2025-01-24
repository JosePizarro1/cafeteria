from django.db import models

class Sede(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.TextField()
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_stock = models.IntegerField(default=0)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name="productos")

    def __str__(self):
        return f"{self.nombre} - {self.sede.nombre}"

    def calcular_ganancia(self):
        return self.precio_venta - self.precio_compra


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
        # Actualizar stock del producto
        self.producto.cantidad_stock -= self.cantidad
        self.producto.save()


class Kardex(models.Model):
    MOVIMIENTO_CHOICES = [
        ('IN', 'Ingreso'),
        ('OUT', 'Salida'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="kardex")
    fecha = models.DateTimeField(auto_now_add=True)
    movimiento = models.CharField(max_length=3, choices=MOVIMIENTO_CHOICES)
    cantidad = models.IntegerField()
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Kardex {self.producto.nombre} - {self.movimiento} ({self.fecha.strftime('%Y-%m-%d')})"
