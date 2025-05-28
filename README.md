# Forrajería Mimitos - Sitio Web

Este es el sitio web oficial de Forrajería Mimitos, una tienda especializada en productos para mascotas ubicada en Luján, Buenos Aires.

## Características

- Catálogo de productos con filtrado por categorías
- Búsqueda de productos en tiempo real
- Información de sucursales con mapas interactivos
- Diseño responsive y moderno
- Integración con WhatsApp para consultas

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/Piroenzo/Mimitos.github.io.git
cd Mimitos.github.io
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución Local

Para ejecutar el proyecto localmente:

```bash
python app.py
```

El sitio estará disponible en `http://localhost:5000`

## Despliegue en Render

1. Crear una cuenta en [Render](https://render.com)
2. Conectar el repositorio de GitHub
3. Crear un nuevo Web Service
4. Configurar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Python Version: 3.8 o superior

## Estructura del Proyecto

```
Mimitos.github.io/
├── static/          # Archivos estáticos (CSS, JS, imágenes)
├── templates/       # Plantillas HTML
├── app.py          # Aplicación principal
├── requirements.txt # Dependencias del proyecto
└── README.md       # Este archivo
```

## Tecnologías Utilizadas

- Flask (Backend)
- HTML5, CSS3, JavaScript (Frontend)
- Google Maps API (Mapas interactivos)
- Font Awesome (Iconos)
- Google Fonts (Tipografía)

## Contacto

Para soporte o consultas:
- WhatsApp: [2323-534156](https://wa.me/5492323534156)
- Instagram: [@mimitos.balanceados](https://instagram.com/mimitos.balanceados)

## Licencia

Todos los derechos reservados © 2024 Forrajería Mimitos 