from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def login(request):
    return render(request, 'login.html')


def home(request):
    return render(request, 'index.html')

# Vista para el Dashboard
def dashboard(request):
    return render(request, 'dashboard.html')

# Vista para la lista de productos
def productos_list(request):
    return render(request, 'productos_list.html')

# Vista para la lista de sedes
def sedes_list(request):
    return render(request, 'sedes_list.html')

# Vista para crear una nueva sede
def sedes_create(request):
    return render(request, 'sedes_create.html')

# Vista para la lista de ventas
def ventas_list(request):
    return render(request, 'ventas_list.html')

# Vista para crear una nueva venta
def ventas_create(request):
    return render(request, 'ventas_create.html')

# Vista para el Kardex
def kardex_list(request):
    return render(request, 'kardex_list.html')

# Vista para los reportes
def reportes(request):
    return render(request, 'reportes.html')

