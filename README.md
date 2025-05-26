# Mimitos Web

Sitio web para la tienda de mascotas Mimitos, desarrollado con Flask.

## Características

- Catálogo de productos
- Sistema de autenticación de usuarios
- Panel de administración
- Gestión de productos y categorías
- Sistema de notificaciones por email

## Requisitos

- Python 3.8 o superior
- Flask 3.0.0
- SQLAlchemy
- Gunicorn (para producción)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/mimitos_web.git
cd mimitos_web
```

2. Crear y activar el entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
Crear un archivo `.env` con las siguientes variables:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña
```

5. Iniciar la aplicación:
```bash
flask run
```

## Estructura del Proyecto

```
mimitos_web/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── static/            # Archivos estáticos (CSS, JS, imágenes)
├── templates/         # Plantillas HTML
├── logs/             # Archivos de registro
└── backups/          # Copias de seguridad
```

## Despliegue

El proyecto está configurado para ser desplegado en Render. Para desplegar:

1. Subir el código a GitHub
2. Crear un nuevo servicio Web en Render
3. Conectar con el repositorio de GitHub
4. Configurar las variables de entorno en Render

## Licencia

Este proyecto está bajo la Licencia MIT. 