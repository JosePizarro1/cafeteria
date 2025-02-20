from django.shortcuts import render
from django.http import HttpResponse
from .models import Producto, ProductoSede, Sede ,Venta, DetalleVenta, Kardex ,Cliente,Rol
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Sum, F
from datetime import datetime,timedelta
import calendar
from django.contrib.auth.models import User
from datetime import date
from django.utils.dateparse import parse_date

def lista_deudores(request):
    """Muestra las ventas no pagadas."""
    ventas = Venta.objects.filter(cancelada=False)
    return render(request, "deudores.html", {"ventas": ventas})
    

def detalle_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = DetalleVenta.objects.filter(venta=venta)
    data = [
        {
            "producto": detalle.producto.nombre,  # ✅ Ahora devuelve el nombre del producto
            "cantidad": detalle.cantidad,
            "precio_unitario": float(detalle.precio_unitario),
            "subtotal": float(detalle.subtotal),
        }
        for detalle in detalles
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def marcar_venta_pagada(request, venta_id):
    """Marca una venta como pagada (cancelada=True)."""
    venta = get_object_or_404(Venta, id=venta_id)
    venta.cancelada = True
    venta.save()
    return JsonResponse({"status": "success"})    
    
    
    
    
def inventario(request):
    kardex_movimientos = Kardex.objects.all().order_by('-fecha')
    sedes = Sede.objects.all() if request.user.rol.es_admin else None

    return render(request, 'inventario.html', {
        'kardex_movimientos': kardex_movimientos,
        'sedes': sedes
    })
    
def crear_cliente(request):
    nombre = request.GET.get('nombre')
    telefono = request.GET.get('telefono')

    if nombre:  # Validar que al menos el nombre esté presente
        cliente, created = Cliente.objects.get_or_create(nombre=nombre, defaults={'telefono': telefono})
        
        if created:
            return JsonResponse({"mensaje": "Cliente creado exitosamente", "id": cliente.id}, status=201)
        else:
            return JsonResponse({"mensaje": "El cliente ya existe"}, status=200)
    
    return JsonResponse({"error": "Faltan datos"}, status=400)
    
@csrf_exempt  # Permite realizar solicitudes POST desde el frontend.
def guardar_usuario(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            confirm_password = data.get('confirm_password')

            if not username or not password or not confirm_password:
                return JsonResponse({'error': 'Todos los campos son obligatorios.'}, status=400)

            if password != confirm_password:
                return JsonResponse({'error': 'Las contraseñas no coinciden.'}, status=400)

            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'El usuario ya existe.'}, status=400)

            # Crear el usuario
            user = User.objects.create_user(username=username, password=password)
            user.save()

            return JsonResponse({'message': 'Usuario creado exitosamente.'}, status=201)

        except Exception as e:
            return JsonResponse({'error': f'Ocurrió un error: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Método no permitido.'}, status=405)
    
def ventas_list(request):
    # Obtenemos todas las ventas
    ventas = Venta.objects.all().order_by('-fecha')

    # Verificamos si el usuario tiene un rol
    if request.user.rol:
        # Si el usuario es admin, verificamos si tiene una sede
        if request.user.rol.es_admin:
            # Solo intentamos acceder a 'all()' si 'sede' no es None
            sedes = request.user.rol.sede.all() if request.user.rol.sede else []
        else:
            sedes = [request.user.rol.sede]  # Si no es admin, solo asigna su sede

        # Filtrar ventas si el usuario no es admin
        if not request.user.rol.es_admin:
            ventas = ventas.filter(sede=request.user.rol.sede)
    else:
        sedes = []  # Si no tiene rol, no hay sedes

    # Pasamos las ventas al contexto
    context = {
        'ventas': ventas,
        'sedes': sedes,
    }

    # Renderizamos la plantilla
    return render(request, 'ventas_list.html', context)
    
    
def registrar_venta(request):
    if request.method == 'POST':
        try:
            metodo_pago = request.POST.get('metodo_pago')
            sede_id = request.POST.get('sede')  # ID de la sede
            cliente_id = request.POST.get('cliente')  # ID del cliente, puede ser None
            productos = request.POST.getlist('producto[]')  # IDs de los productos
            cantidades = request.POST.getlist('cantidad[]')  # Cantidades de los productos

            if not sede_id or not productos or not cantidades or not metodo_pago:
                return JsonResponse({
                    "status": "error",
                    "message": "Todos los campos son obligatorios."
                }, status=400)
            valor=True
            # Validar cliente si el método de pago es crédito
            cliente = None
            if metodo_pago == 'CR':
                if not cliente_id:
                    return JsonResponse({
                        "status": "error",
                        "message": "Debe seleccionar un cliente si el método de pago es Crédito."
                    }, status=400)
                cliente = get_object_or_404(Cliente, id=cliente_id)
                valor=False
            # Obtener la sede
            sede = get_object_or_404(Sede, id=sede_id)

            # Crear la venta
            venta = Venta.objects.create(
                sede=sede,
                metodo_pago=metodo_pago,
                cliente=cliente,  # Se guarda el cliente solo si aplica
                cancelada=valor
            )

            # Procesar los detalles de la venta
            total = 0
            for producto_id, cantidad in zip(productos, cantidades):
                producto = get_object_or_404(Producto, id=producto_id)
                cantidad = int(cantidad)

                # Verificar stock
                producto_sede = get_object_or_404(ProductoSede, producto=producto, sede=sede)
                if cantidad > producto_sede.cantidad_stock:
                    venta.delete()  # Eliminar la venta si hay error
                    return JsonResponse({
                        "status": "error",
                        "message": f"No hay suficiente stock de {producto.nombre}."
                    }, status=400)

                # Calcular subtotal y crear detalle de venta
                subtotal = cantidad * producto.precio_venta
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta,
                    subtotal=subtotal
                )

                # Actualizar stock en la sede
                producto_sede.cantidad_stock -= cantidad
                producto_sede.save()

                # Registrar movimiento en el kardex
                Kardex.objects.create(
                    producto=producto,
                    sede=sede,
                    movimiento='OUT',
                    cantidad=cantidad,
                    observacion=f"Venta ID {venta.id}"
                )

                total += subtotal

            # Actualizar el total de la venta
            venta.total = total
            venta.save()

            return JsonResponse({
                "status": "success",
                "message": f"Venta registrada exitosamente.",
                "data": {
                    "venta_id": venta.id,
                    "total": total
                }
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Ocurrió un error al procesar la venta: {str(e)}"
            }, status=500)

    return JsonResponse({
        "status": "error",
        "message": "Método no permitido."
    }, status=405)
    
def productos_por_sede(request):
    if 'sede_id' in request.GET:
        sede_id = request.GET.get('sede_id')
        try:
            # Filtrar productos disponibles para la sede seleccionada
            productos_sede = ProductoSede.objects.filter(sede_id=sede_id, cantidad_stock__gt=0)
            productos = [
                {
                    'id': producto.producto.id,
                    'nombre': producto.producto.nombre,
                    'precio': producto.producto.precio_venta,
                    'stock': producto.cantidad_stock,  # Cambiar stock por cantidad_stock
                }
                for producto in productos_sede
            ]
            return JsonResponse({'productos': productos}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Solicitud inválida'}, status=400)

    
def registrar_entrada(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_entrada')  # ID del producto
        cantidad_entrada = int(request.POST.get('cantidad_entrada', 0))  # Cantidad a agregar
        sede_id = request.POST.get('sede_id')  # ID de la sede

        # Verificar que los campos no estén vacíos
        if not producto_id or not cantidad_entrada :
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('kardex_list')

        # Obtener el producto y la sede
        producto = get_object_or_404(Producto, id=producto_id)
        # Sumar la cantidad al stock del producto
        producto.cantidad_stock += cantidad_entrada
        producto.save()

        # Registrar en el Kardex
        Kardex.objects.create(
            producto=producto,
            movimiento='IN',
            cantidad=cantidad_entrada,
            observacion=f"Ingreso de {cantidad_entrada} unidades al inventario."
        )

        # Mensaje de éxito
        messages.success(
            request,
            f"Se agregaron {cantidad_entrada} unidades al stock de {producto.nombre}."
        )
        return redirect('kardex_list')

    return redirect('kardex_list')  # Manejo para peticiones GET no permitidas
    
def obtener_cantidad_disponible(request):
    if request.method == 'GET':
        producto_id = request.GET.get('producto_id')  # Obtener el ID del producto desde la solicitud
        try:
            producto = Producto.objects.get(id=producto_id)  # Buscar el producto en la base de datos
            return JsonResponse({'success': True, 'cantidad_actual': producto.cantidad_stock})  # Devolver la cantidad de stock
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Producto no encontrado.'})  # Manejar producto inexistente
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})  # Manejar método no permitido
    
def transferir_productos(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_transferencia')  # ID del producto
        cantidad_transferir = int(request.POST.get('cantidad_transferencia', 0))  # Cantidad a transferir
        sede_destino_id = request.POST.get('sede_transferencia')  # ID de la sede destino

        # Verificar que los campos no estén vacíos
        if not producto_id or not cantidad_transferir or not sede_destino_id:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect('kardex_list')

        # Obtener el producto general
        producto = get_object_or_404(Producto, id=producto_id)

        # Verificar si la cantidad a transferir no supera el stock disponible en el producto general
        if cantidad_transferir > producto.cantidad_stock:
            messages.error(
                request,
                f"No se puede transferir. Stock disponible en producto: {producto.cantidad_stock}."
            )
            return redirect('kardex_list')

        # Descontar la cantidad transferida del stock del producto general
        producto.cantidad_stock -= cantidad_transferir
        producto.save()

        # Obtener la sede destino
        sede_destino = get_object_or_404(Sede, id=sede_destino_id)

        # Verificar si el producto ya existe en la sede destino
        producto_sede_destino, creado = ProductoSede.objects.get_or_create(
            producto=producto,
            sede=sede_destino,
            defaults={'cantidad_stock': 0}  # Si no existe, crea con stock inicial 0
        )

        # Si el producto ya existe en la sede destino, actualizar el stock sumando la cantidad transferida
        if not creado:
            producto_sede_destino.cantidad_stock += cantidad_transferir
            producto_sede_destino.save()
        else:
            # Si el producto es nuevo en la sede, establecer la cantidad inicial como la cantidad transferida
            producto_sede_destino.cantidad_stock = cantidad_transferir
            producto_sede_destino.save()

        # Mensaje de éxito
        messages.success(
            request,
            f"Se transfirieron {cantidad_transferir} unidades de {producto.nombre} a {sede_destino.nombre}."
        )
        return redirect('kardex_list')

    return redirect('kardex_list')
    
def obtener_cantidad_actual(request):
    if request.method == 'GET':
        producto_id = request.GET.get('producto_id')
        try:
            producto = Producto.objects.get(id=producto_id)
            return JsonResponse({'success': True, 'cantidad_actual': producto.cantidad_stock})
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Producto no encontrado.'})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

def logout_view(request):
    logout(request)  # Esta función desloguea al usuario actual
    return redirect('login')
    
def productos_create(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            precio_compra = request.POST.get('precio_compra')
            precio_venta = request.POST.get('precio_venta')
            cantidad_stock = request.POST.get('cantidad_stock')
            # Crear el producto
            Producto.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                precio_compra=precio_compra,
                precio_venta=precio_venta,
                cantidad_stock=cantidad_stock
            )

            messages.success(request, 'Producto creado con éxito.')
            return redirect('productos_list')  # Redirigir a la lista de productos

        except Exception as e:
            messages.error(request, f'Ocurrió un error: {str(e)}')

    sedes = Sede.objects.all()  # Obtener todas las sedes para el formulario
    return render(request, 'productos_create.html', {'sedes': sedes})
def crear_usuario(request):
    return render(request, 'crear_usuario.html')
def obtener_usuario_info(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=400)

    usuario = User.objects.filter(username=username).first()
    if not usuario:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=400)

    # Obtener el rol y sede del usuario
    rol = Rol.objects.filter(usuario=usuario).first()
    sede = rol.sede if rol else None

    return JsonResponse({
        'es_admin': rol.es_admin if rol else False,
        'es_usuario': rol.es_usuario if rol else False,
        'sede_id': sede.id if sede else None
    })
def asignar_rol_sede(request):
    """
    Vista para renderizar la página de asignación de roles y sede.
    """
    usuarios = User.objects.all()  # Obtener todos los usuarios
    sedes = Sede.objects.all()  # Obtener todas las sedes disponibles
    roles = Rol.objects.all()  # Obtener todos los roles

    usuarios_info = []
    # Pasar la información procesada al template
    return render(request, 'asignar_rol_sede.html', {
        'usuarios_info': usuarios,
        'sedes': sedes,
    })
    
def guardar_roles(request):
    """
    Vista para guardar los roles y sede asignados a un usuario.
    """
    if request.method == "POST":
        try:
            # Recibimos los datos JSON desde el frontend
            data = json.loads(request.body)
            username = data.get('username')
            es_admin = data.get('es_admin')
            es_usuario = data.get('es_usuario')
            sede_id = data.get('sede_id')

            # Validar que el username esté presente
            if not username:
                return JsonResponse({"error": "Usuario no proporcionado"}, status=400)

            # Obtener el usuario con el username
            usuario = get_object_or_404(User, username=username)

            # Obtener el rol asociado al usuario
            rol = get_object_or_404(Rol, usuario=usuario)

            # Actualizar los campos del rol
            rol.es_admin = es_admin
            rol.es_usuario = es_usuario

            # Verificar si existe una sede y asignarla
            sede = Sede.objects.get(id=sede_id) if sede_id else None
            rol.sede = sede

            # Guardar los cambios en el rol
            rol.save()

            # Respuesta de éxito
            return JsonResponse({"message": "Roles y sede asignados correctamente!"})

        except Sede.DoesNotExist:
            # Si la sede no existe
            return JsonResponse({"error": "Sede no encontrada"}, status=404)
        except Exception as e:
            # Manejo de excepciones generales
            return JsonResponse({"error": f"Ocurrió un error: {str(e)}"}, status=400)

    # Si el método no es POST, devolvemos un error
    return JsonResponse({"error": "Método no permitido"}, status=405)   
    
def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')  # Redirige a 'home' si las credenciales son válidas
        else:
            # Pasamos el mensaje de error como parte de los mensajes del contexto
            messages.error(request, "Usuario o contraseña incorrectos")
    return render(request, 'login.html')

def home(request):
    return render(request, 'index.html')

def dashboard(request):
    # Fecha actual y año actual
    today = datetime.now()
    year = today.year

    # Calcular ganancias del día actual
    ganancia_dia = DetalleVenta.objects.filter(
        venta__fecha__date=today.date()
    ).annotate(
        ganancia=F('cantidad') * (F('precio_unitario') - F('producto__precio_compra'))
    ).aggregate(
        total_ganancia=Sum('ganancia')
    )['total_ganancia'] or 0

    # Calcular ganancias del mes actual
    ganancia_mes = DetalleVenta.objects.filter(
        venta__fecha__month=today.month,
        venta__fecha__year=year
    ).annotate(
        ganancia=F('cantidad') * (F('precio_unitario') - F('producto__precio_compra'))
    ).aggregate(
        total_ganancia=Sum('ganancia')
    )['total_ganancia'] or 0

    # Generar datos de ganancias mensuales para cada sede
    ganancias_sede_1 = []
    ganancias_sede_2 = []
    meses = [calendar.month_name[i] for i in range(1, 13)]  # Nombres de los 12 meses

    for mes in range(1, 13):
        # Ganancias mensuales para sede 1
        ganancia_sede_1 = DetalleVenta.objects.filter(
            venta__fecha__month=mes,
            venta__fecha__year=year,
            venta__sede_id=1
        ).annotate(
            ganancia=F('cantidad') * (F('precio_unitario') - F('producto__precio_compra'))
        ).aggregate(
            total_ganancia=Sum('ganancia')
        )['total_ganancia'] or 0
        ganancias_sede_1.append(ganancia_sede_1)

        # Ganancias mensuales para sede 2
        ganancia_sede_2 = DetalleVenta.objects.filter(
            venta__fecha__month=mes,
            venta__fecha__year=year,
            venta__sede_id=2
        ).annotate(
            ganancia=F('cantidad') * (F('precio_unitario') - F('producto__precio_compra'))
        ).aggregate(
            total_ganancia=Sum('ganancia')
        )['total_ganancia'] or 0
        ganancias_sede_2.append(ganancia_sede_2)

    # Contar cantidad de productos
    productos_count = Producto.objects.count()

    # Calcular ganancias en crédito (según 'metodo_pago' en lugar de 'tipo_pago')
    ventas_credito = Venta.objects.filter(metodo_pago='CR', cancelada=False).aggregate(total=Sum('total'))['total'] or 0

    # Obtener ganancias por sede
    ganancias_sede = {}
    for sede in Sede.objects.all():
        ganancias_sede[sede.nombre] = Venta.objects.filter(sede=sede, fecha__month=datetime.now().month).aggregate(total=Sum('total'))['total'] or 0

    # Datos para el gráfico de ventas por sede
    sedes = list(ganancias_sede.keys())  # Lista de nombres de las sedes
    ganancias = list(ganancias_sede.values())  # Lista de ganancias por sede

    # Obtener las fechas del mes actual
    dias_mes = [datetime.now().replace(day=1) + timedelta(days=i) for i in range(0, 31)]  # Para los primeros 31 días
    fechas = [dia.strftime('%d-%m-%Y') for dia in dias_mes]  # Formato: Día-Mes-Año

    # Calcular las ganancias diarias del mes
    ganancias_diarias = []
    for dia in dias_mes:
        ganancias_dia = Venta.objects.filter(fecha__date=dia).aggregate(total=Sum('total'))['total'] or 0
        ganancias_diarias.append(ganancias_dia)
    # Convertir Decimal a float para evitar errores en JavaScript
    ganancias_sede_1 = [float(ganancia) for ganancia in ganancias_sede_1]
    ganancias_sede_2 = [float(ganancia) for ganancia in ganancias_sede_2]
    # Preparar el contexto para el template
    context = {
        'ganancia_dia': ganancia_dia,
        'ganancia_mes': ganancia_mes,
        'productos_count': productos_count,
        'ventas_credito': ventas_credito,
        'sedes': sedes,
        'ganancias': ganancias,
        'meses': meses,
        'ganancias_sede_1': ganancias_sede_1,
        'ganancias_sede_2': ganancias_sede_2,
        'fechas': fechas,  # Fechas del mes
        'ganancias_diarias': ganancias_diarias,  # Ganancias diarias
    }

    return render(request, 'dashboard.html', context)
    
def editar_producto(request, producto_id):
    if request.method == 'POST':
        # Obtener el producto desde la base de datos
        producto = get_object_or_404(Producto, id=producto_id)

        # Obtener los datos enviados en el formulario
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio_compra = request.POST.get('precio_compra')
        precio_venta = request.POST.get('precio_venta')

        try:
            # Actualizar los datos del producto
            producto.nombre = nombre
            producto.descripcion = descripcion
            producto.precio_compra = precio_compra
            producto.precio_venta = precio_venta
            producto.save()

            # Responder con éxito
            return JsonResponse({'success': True, 'message': 'Producto actualizado correctamente'})

        except Exception as e:
            # Si ocurre algún error al guardar, responder con error
            return JsonResponse({'success': False, 'message': str(e)})

    # Si no es un POST, se retorna un error
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    
def eliminar_producto(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    
    # Verificar si el producto está asociado a alguna sede
    if ProductoSede.objects.filter(producto=producto).exists():
        messages.error(request, 'No se puede eliminar el producto porque está asociado a una sede.')
        return redirect('productos_list')

    # Si no está asociado a ninguna sede, eliminar el producto
    producto.delete()
    messages.success(request, 'Producto eliminado exitosamente.')
    return redirect('productos_list')
def productos_list(request):
    # Obtener todos los productos de la base de datos
    productos = Producto.objects.all()
    # Pasar los productos al contexto para renderizar en el template
    context = {'productos': productos}
    return render(request, 'productos_list.html', context)

# Vista para la lista de sedes
def sedes_list(request):
    return render(request, 'sedes_list.html')

# Vista para crear una nueva sede
def sedes_create(request):
    return render(request, 'sedes_create.html')



def ventas_create(request):
    # Obtener todas las sedes, productos y clientes
    sedes = Sede.objects.all()
    productos = Producto.objects.all()
    clientes = Cliente.objects.all()  # Asegúrate de que el modelo Cliente esté definido

    # Enviar los datos al contexto
    context = {
        'sedes': sedes,
        'productos': productos,
        'clientes': clientes,  # Añadimos los clientes al contexto
    }
    return render(request, 'ventas_create.html', context)


def kardex_list(request):
    productos = Producto.objects.all()
    sedes = Sede.objects.all()
    context = {
        'productos': productos,
        'sedes': sedes,
    }
    return render(request, 'kardex_list.html', context)

def reportes(request):
    fecha_str = request.GET.get('fecha', '')  # Capturar la fecha desde la URL
    fecha = parse_date(fecha_str) if fecha_str else date.today()  # Convertir a formato de fecha

    # Ventas del día (con filtro por fecha)
    ventas = Venta.objects.filter(fecha__date=fecha)

    # Consulta para obtener el stock por sede
    kardex = ProductoSede.objects.filter(
        sede_id__in=[1, 2]
    ).select_related('producto', 'sede').values(
        'producto__nombre', 'sede__nombre', 'cantidad_stock'
    )

    # Organizar los productos por sede y agregar stock principal
    productos_kardex = {}
    for item in kardex:
        producto_nombre = item['producto__nombre']
        sede_nombre = item['sede__nombre']
        cantidad_stock = item['cantidad_stock']

        # Verificar si el producto ya existe en el diccionario
        if producto_nombre not in productos_kardex:
            # Se añade el stock principal (de Producto)
            stock_principal = Producto.objects.get(nombre=producto_nombre).cantidad_stock
            productos_kardex[producto_nombre] = {
                'stock_principal': stock_principal,
                'sede1_stock': 0,
                'sede2_stock': 0
            }

        # Asignar el stock según la sede
        if sede_nombre == 'Egatur':
            productos_kardex[producto_nombre]['sede1_stock'] = cantidad_stock
        elif sede_nombre == 'Focus':
            productos_kardex[producto_nombre]['sede2_stock'] = cantidad_stock

            
    return render(request, 'reportes.html', {
        'fecha_seleccionada': fecha.strftime('%Y-%m-%d') if fecha else '',  # Mantener la fecha
        'ventas': ventas,
        'kardex': productos_kardex,  # Pasamos el diccionario con los stocks por sede

    })


