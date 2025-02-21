# ☕ Sistema de Gestión para Cafetería

Este es un sistema desarrollado en **Django** para gestionar una cafetería. Permite administrar productos, ventas, clientes y reportes de inventario.

## 📌 Características
- Gestión de productos y stock por sede.
- Registro y control de ventas.
- Manejo de clientes y deudas.
- Reportes de ventas y kardex de inventario.

## 📂 Tecnologías Utilizadas
- **Backend:** Django
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Base de Datos:** SQLite (puede cambiarse a PostgreSQL o MySQL)
- **Librerías adicionales:** Select2,Datatable , entre otros 

## 🚀 Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/nombre-del-repositorio.git
cd nombre-del-repositorio
```

### 2️⃣ Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar la base de datos
```bash
python manage.py migrate
python manage.py createsuperuser  # Crear un usuario administrador
```

### 5️⃣ Cargar datos iniciales (opcional)
```bash
python manage.py loaddata datos_iniciales.json
```

### 6️⃣ Ejecutar el servidor
```bash
python manage.py runserver
```

Accede a **http://127.0.0.1:8000/** para usar el sistema.

## 📊 Estructura del Proyecto
```
📂 nombre-del-proyecto/
├── 📂 myapp/                # Aplicación principal
│   ├── 📂 models.py         # Modelos de la base de datos
│   ├── 📂 views.py          # Vistas del sistema
│   ├── 📂 urls.py           # Rutas
│   ├── 📂 templates/        # Archivos HTML
│   └── 📂 static/           # Archivos estáticos (CSS, JS)
├── 📂 media/                # Archivos subidos
├── 📜 manage.py             # Script de administración de Django
└── 📜 requirements.txt      # Dependencias del proyecto
```

## 📜 Licencia
Este proyecto está bajo la licencia **MIT**. Puedes modificarlo y adaptarlo según tus necesidades.

## 📧 Contacto
Si tienes preguntas o sugerencias, contáctame en [josepizarroarca@gmail.com](mailto:josepizarroarca@gmail.com).

