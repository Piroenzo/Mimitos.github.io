from flask import Flask, render_template, request, redirect, flash, jsonify, session, url_for
from flask_mail import Mail, Message
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime, timedelta
from math import ceil
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import json
import hashlib
import shutil
from pathlib import Path

# Configuración de la aplicación
app = Flask(__name__,
           template_folder='templates',
           static_folder='static',
           static_url_path='/static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'mimitos.balanceados@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'lakj dbwp gkdq msbk')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'mimitos.balanceados@gmail.com')
app.config['ADMIN_PASSWORD'] = 'mimitos2024'

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Logging de rutas al inicio
app.logger.info(f'Directorio base: {BASE_DIR}')
app.logger.info(f'Directorio de plantillas: {TEMPLATES_DIR}')
app.logger.info(f'Directorio estático: {STATIC_DIR}')

# Verificar directorios
if not os.path.exists(TEMPLATES_DIR):
    app.logger.error(f'Directorio de plantillas no encontrado: {TEMPLATES_DIR}')
    # Intentar crear el directorio si no existe
    try:
        os.makedirs(TEMPLATES_DIR, exist_ok=True)
        app.logger.info(f'Directorio de plantillas creado: {TEMPLATES_DIR}')
    except Exception as e:
        app.logger.error(f'Error al crear directorio de plantillas: {str(e)}')

if not os.path.exists(STATIC_DIR):
    app.logger.error(f'Directorio estático no encontrado: {STATIC_DIR}')
    # Intentar crear el directorio si no existe
    try:
        os.makedirs(STATIC_DIR, exist_ok=True)
        app.logger.info(f'Directorio estático creado: {STATIC_DIR}')
    except Exception as e:
        app.logger.error(f'Error al crear directorio estático: {str(e)}')

# Listar archivos en directorios
if os.path.exists(TEMPLATES_DIR):
    app.logger.info(f'Archivos en templates: {os.listdir(TEMPLATES_DIR)}')
if os.path.exists(STATIC_DIR):
    app.logger.info(f'Archivos en static: {os.listdir(STATIC_DIR)}')

# Configuración de logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/mimitos.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Mimitos startup')

# Inicialización de Mail
mail = Mail(app)

# Configuración de caché
CACHE_DURATION = timedelta(minutes=5)  # Duración del caché
cache = {}

# Configuración de backup
BACKUP_DIR = 'backups'
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def create_backup():
    """Crea una copia de seguridad de los productos"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'productos_backup_{timestamp}.json')
    
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(productos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        app.logger.error(f"Error al crear backup: {str(e)}")
        return False

def get_cached_data(key):
    """Obtiene datos del caché si están disponibles y no han expirado"""
    if key in cache:
        data, timestamp = cache[key]
        if datetime.now() - timestamp < CACHE_DURATION:
            return data
    return None

def set_cached_data(key, data):
    """Almacena datos en el caché con timestamp"""
    cache[key] = (data, datetime.now())

# Base de datos de productos (en un caso real, esto sería una base de datos)
productos = [
    {
        "id": 1,
        "nombre": "Dog Selection Adulto 21KG",
        "imagen": "img/Dog_Pro_Adulto_x20.jpeg",
        "precio": 45000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 2,
        "nombre": "Dog Selection Cachorro 21KG",
        "imagen": "img/Dog_Pro_Cachorro_x15.jpeg",
        "precio": 48000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para cachorros"
    },
    {
        "id": 3,
        "nombre": "Dog Selection Adulto RP 15KG",
        "imagen": "img/Agility_ad_RPx15.jpeg",
        "precio": 35000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 4,
        "nombre": "Cat Selection 10KG",
        "imagen": "img/Cat_like_Ad_x15.jpeg",
        "precio": 28000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos"
    },
    {
        "id": 5,
        "nombre": "Excellent Gato Adulto 7.5KG",
        "imagen": "img/Cat pro_x_7.5_kg.jpeg",
        "precio": 32000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos adultos"
    },
    {
        "id": 6,
        "nombre": "Excellent Gato Urinario 7.5KG",
        "imagen": "img/Agility_gato_urinary_x10k.jpeg",
        "precio": 35000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos con problemas urinarios"
    },
    {
        "id": 7,
        "nombre": "Excellent Gato Adulto 15KG",
        "imagen": "img/Cat_pro_x15.jpeg",
        "precio": 58000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos adultos"
    },
    {
        "id": 8,
        "nombre": "Cat Chow Gatito 8KG",
        "imagen": "img/Kitten_x7,5k.jpeg",
        "precio": 25000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatitos"
    },
    {
        "id": 9,
        "nombre": "Cat Chow Gatito 15KG",
        "imagen": "img/Perf._Kitten_x7,5k.jpeg",
        "precio": 42000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatitos"
    },
    {
        "id": 10,
        "nombre": "Cat Chow Adulto 8KG",
        "imagen": "img/Perf._Gato_x7,5k.jpeg",
        "precio": 23000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos adultos"
    },
    {
        "id": 11,
        "nombre": "Cat Chow Adulto 15KG",
        "imagen": "img/Performance_adulto_x15k.jpeg",
        "precio": 40000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos adultos"
    },
    {
        "id": 12,
        "nombre": "Dog Chow Cachorro 21KG",
        "imagen": "img/Medium_puppy_x15k.jpeg",
        "precio": 42000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para cachorros"
    },
    {
        "id": 13,
        "nombre": "Dog Chow Adulto 21KG",
        "imagen": "img/Medium_adulto_x15k.jpeg",
        "precio": 38000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 14,
        "nombre": "Chacal 22KG",
        "imagen": "img/Mantenaince_x22kg.jpeg",
        "precio": 35000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros"
    },
    {
        "id": 15,
        "nombre": "Tiernitos Adulto 21KG",
        "imagen": "img/Old_Prince_Tradicional_x20kg.jpeg",
        "precio": 32000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 16,
        "nombre": "Pachá 22KG",
        "imagen": "img/Bred_Dog_Adulto_x20kg.jpeg",
        "precio": 35000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros"
    },
    {
        "id": 17,
        "nombre": "Maxi Adulto 15KG",
        "imagen": "img/Maxi_adulto_x15k.jpeg",
        "precio": 28000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 18,
        "nombre": "Sabrositos Gato Pescado 11KG",
        "imagen": "img/Sabrositos_gato_pescado_x11k.jpeg",
        "precio": 32000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos"
    },
    {
        "id": 19,
        "nombre": "Sabrositos Cachorro 8KG",
        "imagen": "img/Sabrositos_cachorro_x8k.jpeg",
        "precio": 28000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para cachorros"
    },
    {
        "id": 20,
        "nombre": "Sabrositos Cachorro 18KG",
        "imagen": "img/Sabrositos_cachorro_x18k.jpeg",
        "precio": 45000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para cachorros"
    },
    {
        "id": 21,
        "nombre": "Sabrositos Gato 20KG",
        "imagen": "img/Sabrositos_gato_x20k.jpeg",
        "precio": 55000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos"
    },
    {
        "id": 22,
        "nombre": "Sabrositos Gato 10KG",
        "imagen": "img/Sabrositos_gato_x10k.jpeg",
        "precio": 30000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos"
    },
    {
        "id": 23,
        "nombre": "Sabrositos Adulto 15KG",
        "imagen": "img/Sabrositos_cachorro_x18k.jpeg",
        "precio": 35000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 24,
        "nombre": "Sabrositos Adulto 22KG",
        "imagen": "img/Sabrositos_adulto_x22k.jpeg",
        "precio": 48000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 25,
        "nombre": "Biomax Cachorro 15KG",
        "imagen": "img/Biomax_Cach_x15kg.jpeg",
        "precio": 42000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para cachorros"
    },
    {
        "id": 26,
        "nombre": "Biomax Adulto RP 15KG",
        "imagen": "img/Biomax_Adulto_Rp_x15kg.jpeg",
        "precio": 38000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 27,
        "nombre": "Biomax Adulto 20KG",
        "imagen": "img/Biomax_Adulto_x20kg.jpeg",
        "precio": 45000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 28,
        "nombre": "Bred Dog Adulto 20KG",
        "imagen": "img/Bred_Dog_Adulto_x20kg.jpeg",
        "precio": 42000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 29,
        "nombre": "Old Prince Cordero Adulto/Cachorro 15KG",
        "imagen": "img/Old_Prince_Cordero_Adulto_Cach_x15kg.jpeg",
        "precio": 55000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos y cachorros"
    },
    {
        "id": 30,
        "nombre": "Old Prince Cordero Adulto RP 15KG",
        "imagen": "img/Old_Prince_Cordero_Adulto_Rp_x15kg.jpeg",
        "precio": 52000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 31,
        "nombre": "Old Prince Cordero Adulto 15KG",
        "imagen": "img/Old_Prince_Cordero_Adulto_x15kg.jpeg",
        "precio": 55000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 32,
        "nombre": "Old Prince Tradicional 20KG",
        "imagen": "img/Old_Prince_Tradicional_x20kg.jpeg",
        "precio": 48000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 33,
        "nombre": "Mantenaince 22KG",
        "imagen": "img/Mantenaince_x22kg.jpeg",
        "precio": 42000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 34,
        "nombre": "Kitten 7.5KG",
        "imagen": "img/Kitten_x7,5k.jpeg",
        "precio": 28000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatitos"
    },
    {
        "id": 35,
        "nombre": "Urinary Care 7.5KG",
        "imagen": "img/URINARY_CARE x7,5k.jpeg",
        "precio": 32000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos con problemas urinarios"
    },
    {
        "id": 36,
        "nombre": "Urinary S-O 7.5KG",
        "imagen": "img/URINARY_S-O_x7,5k.jpeg",
        "precio": 32000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos con problemas urinarios"
    },
    {
        "id": 37,
        "nombre": "Urinary Perro 10KG",
        "imagen": "img/URINARY_perro_10k.jpeg",
        "precio": 38000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros con problemas urinarios"
    },
    {
        "id": 38,
        "nombre": "Mini Puppy 15KG",
        "imagen": "img/Mini_puppy_x15k.jpeg",
        "precio": 45000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para cachorros"
    },
    {
        "id": 39,
        "nombre": "Mini Puppy 7.5KG",
        "imagen": "img/Mini_puppy_x7.5k.jpeg",
        "precio": 28000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para cachorros"
    },
    {
        "id": 40,
        "nombre": "Mini Adulto 7.5KG",
        "imagen": "img/Mini_adulto_x7.5k.jpeg",
        "precio": 26000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 41,
        "nombre": "Fit 32 15KG",
        "imagen": "img/FIT_32_x15k.jpeg",
        "precio": 42000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 42,
        "nombre": "Fit 32 7.5KG",
        "imagen": "img/FIT_32_x7,5k .jpeg",
        "precio": 28000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 43,
        "nombre": "Performance Gato 7.5KG",
        "imagen": "img/Perf._Gato_x7,5k.jpeg",
        "precio": 30000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatos adultos"
    },
    {
        "id": 44,
        "nombre": "Performance Kitten 7.5KG",
        "imagen": "img/Perf._Kitten_x7,5k.jpeg",
        "precio": 32000,
        "categoria": "gatos",
        "descripcion": "Alimento balanceado para gatitos"
    },
    {
        "id": 45,
        "nombre": "Performance Junior 15KG",
        "imagen": "img/Performance_junior_x15k.jpeg",
        "precio": 45000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros jóvenes"
    },
    {
        "id": 46,
        "nombre": "Performance Adulto 15KG",
        "imagen": "img/Performance_adulto_x15k.jpeg",
        "precio": 42000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 47,
        "nombre": "Performance Adulto 20KG",
        "imagen": "img/Performance_adultox20k.jpeg",
        "precio": 48000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    },
    {
        "id": 48,
        "nombre": "Medium Puppy 15KG",
        "imagen": "img/Medium_puppy_x15k.jpeg",
        "precio": 45000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para cachorros"
    },
    {
        "id": 49,
        "nombre": "Medium Adulto 15KG",
        "imagen": "img/Medium_adulto_x15k.jpeg",
        "precio": 42000,
        "categoria": "perros",
        "descripcion": "Alimento balanceado para perros adultos"
    }
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Por favor, inicia sesión para acceder a esta página')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    try:
        # Verificar que la plantilla existe
        template_path = os.path.join(TEMPLATES_DIR, 'index.html')
        app.logger.info(f'Buscando plantilla en: {template_path}')
        
        if not os.path.exists(template_path):
            app.logger.error(f'Plantilla index.html no encontrada en: {template_path}')
            # Intentar buscar en otras ubicaciones comunes
            alternative_paths = [
                os.path.join(BASE_DIR, 'templates', 'index.html'),
                os.path.join(os.getcwd(), 'templates', 'index.html'),
                'templates/index.html',
                '/opt/render/project/src/templates/index.html'
            ]
            for path in alternative_paths:
                app.logger.info(f'Intentando ruta alternativa: {path}')
                if os.path.exists(path):
                    app.logger.info(f'Plantilla encontrada en ruta alternativa: {path}')
                    template_path = path
                    break
            else:
                # Si no se encuentra la plantilla, intentar renderizar directamente
                try:
                    return render_template('index.html',
                                         productos=[],
                                         pagina=1,
                                         paginas=1,
                                         busqueda='')
                except Exception as template_error:
                    app.logger.error(f'Error al renderizar plantilla: {str(template_error)}')
                    return render_template('error.html', error="Error de configuración del servidor"), 500

        page = request.args.get('page', 1, type=int)
        busqueda = request.args.get('q', '')
        per_page = 12

        # Validar página
        if page < 1:
            page = 1

        # Intentar obtener datos del caché
        cache_key = f'index_{page}_{busqueda}'
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            try:
                return render_template('index.html', 
                                     productos=cached_data['productos'],
                                     pagina=page,
                                     paginas=cached_data['total_pages'],
                                     busqueda=busqueda)
            except Exception as template_error:
                app.logger.error(f'Error al renderizar plantilla desde caché: {str(template_error)}')
                # Limpiar caché en caso de error
                if cache_key in cache:
                    del cache[cache_key]

        # Si no hay caché o hubo error, calcular los datos
        if busqueda:
            productos_filtrados = [p for p in productos if busqueda.lower() in p['nombre'].lower()]
        else:
            productos_filtrados = productos

        # Validar y limpiar productos
        productos_validos = []
        for producto in productos_filtrados:
            try:
                # Validar precio
                if not isinstance(producto.get('precio'), (int, float)) or producto.get('precio') < 0:
                    producto['precio'] = 0
                    app.logger.warning(f"Precio inválido para producto {producto.get('id')}: {producto.get('precio')}")

                # Validar imagen
                imagen_path = os.path.join(STATIC_DIR, producto.get('imagen', ''))
                app.logger.info(f'Verificando imagen: {imagen_path}')
                if not os.path.exists(imagen_path):
                    app.logger.warning(f"Imagen no encontrada para producto {producto.get('id')}: {producto.get('imagen')}")
                    continue

                # Validar campos requeridos
                if not all(key in producto for key in ['id', 'nombre', 'precio', 'categoria', 'imagen']):
                    app.logger.warning(f"Producto {producto.get('id')} falta campos requeridos")
                    continue

                productos_validos.append(producto)
            except Exception as e:
                app.logger.error(f"Error procesando producto {producto.get('id')}: {str(e)}")
                continue

        # Calcular paginación
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        productos_pagina = productos_validos[start_idx:end_idx]
        total_pages = ceil(len(productos_validos) / per_page) if productos_validos else 1

        # Guardar en caché solo si hay productos válidos
        if productos_validos:
            cache_data = {
                'productos': productos_pagina,
                'total_pages': total_pages
            }
            set_cached_data(cache_key, cache_data)

        try:
            return render_template('index.html',
                                 productos=productos_pagina,
                                 pagina=page,
                                 paginas=total_pages,
                                 busqueda=busqueda)
        except Exception as template_error:
            app.logger.error(f'Error al renderizar plantilla: {str(template_error)}')
            return render_template('error.html', error="Error al mostrar la página"), 500

    except Exception as e:
        app.logger.error(f'Error en la página principal: {str(e)}')
        return render_template('error.html', error="Ha ocurrido un error inesperado"), 500

@app.route('/productos/<categoria>')
def productos_categoria(categoria):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 12  # Número de productos por página
        
        # Filtrar productos por categoría
        productos_filtrados = [p for p in productos if p['categoria'] == categoria]
        
        # Calcular el índice inicial y final para la paginación
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Obtener los productos para la página actual
        productos_pagina = productos_filtrados[start_idx:end_idx]
        
        # Calcular el número total de páginas
        total_pages = ceil(len(productos_filtrados) / per_page)
        
        return render_template('index.html', 
                             productos=productos_pagina,
                             pagina=page,
                             paginas=total_pages,
                             categoria_actual=categoria)
    except Exception as e:
        app.logger.error(f'Error al filtrar productos: {str(e)}')
        return render_template('error.html', error="Error al filtrar productos"), 500

@app.route('/buscar')
def buscar_productos():
    try:
        query = request.args.get('q', '').lower()
        page = request.args.get('page', 1, type=int)
        per_page = 12

        # Filtrar productos que coincidan con la búsqueda
        productos_filtrados = [
            p for p in productos 
            if query in p['nombre'].lower() or 
               query in str(p['precio']).lower()
        ]

        # Calcular paginación
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        productos_pagina = productos_filtrados[start_idx:end_idx]
        total_pages = ceil(len(productos_filtrados) / per_page)

        return render_template('index.html',
                             productos=productos_pagina,
                             pagina=page,
                             paginas=total_pages,
                             busqueda=query)
    except Exception as e:
        app.logger.error(f'Error en la búsqueda: {str(e)}')
        return render_template('error.html', error="Error al buscar productos"), 500

@app.route('/productos_ajax')
def productos_ajax():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 12

        # Intentar obtener datos del caché
        cache_key = f'productos_ajax_{page}'
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            return jsonify(cached_data)

        # Si no hay caché, calcular los datos
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        productos_pagina = productos[start_idx:end_idx]
        total_pages = ceil(len(productos) / per_page)

        html = render_template('_productos.html',
                             productos=productos_pagina)
        
        paginacion = render_template('_paginacion.html',
                                   pagina=page,
                                   paginas=total_pages)
        
        response_data = {
            'html': html,
            'paginacion': paginacion,
            'total_pages': total_pages,
            'current_page': page
        }

        # Guardar en caché
        set_cached_data(cache_key, response_data)
        
        return jsonify(response_data)
    except Exception as e:
        app.logger.error(f'Error en la paginación AJAX: {str(e)}')
        return jsonify({'error': 'Error al cargar productos'}), 500

@app.route('/buscar_ajax')
def buscar_productos_ajax():
    try:
        query = request.args.get('q', '').lower()
        page = request.args.get('page', 1, type=int)
        per_page = 12

        # Filtrar productos que coincidan con la búsqueda
        productos_filtrados = [
            p for p in productos 
            if query in p['nombre'].lower() or 
               query in str(p['precio']).lower()
        ]

        # Calcular paginación
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        productos_pagina = productos_filtrados[start_idx:end_idx]
        total_pages = ceil(len(productos_filtrados) / per_page)

        # Renderizar solo la sección de productos
        html = render_template('_productos.html',
                             productos=productos_pagina)
        
        # Renderizar la paginación
        paginacion = render_template('_paginacion.html',
                                   pagina=page,
                                   paginas=total_pages,
                                   busqueda=query)
        
        return jsonify({
            'html': html,
            'paginacion': paginacion,
            'total_pages': total_pages,
            'current_page': page
        })
    except Exception as e:
        app.logger.error(f'Error en la búsqueda AJAX: {str(e)}')
        return jsonify({'error': 'Error al buscar productos'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Página no encontrada"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Error interno del servidor"), 500

@app.route('/contacto', methods=['POST'])
def enviar_contacto():
    try:
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        mensaje = request.form.get('mensaje')
        
        # Crear el mensaje
        msg = Message(
            subject=f'Nuevo mensaje de contacto de {nombre}',
            recipients=['enzopiro80@gmail.com'],
            body=f'''
            Nombre: {nombre}
            Email: {email}
            Teléfono: {telefono}
            
            Mensaje:
            {mensaje}
            '''
        )
        
        # Enviar el email
        mail.send(msg)
        
        app.logger.info(f'Email de contacto enviado por {nombre}')
        return jsonify({'success': True, 'message': 'Mensaje enviado correctamente'})
        
    except Exception as e:
        app.logger.error(f'Error al enviar email de contacto: {str(e)}')
        return jsonify({'success': False, 'message': 'Error al enviar el mensaje'}), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            flash('Bienvenido al panel de administración')
            return redirect(url_for('admin_panel'))
        else:
            flash('Credenciales inválidas')
    
    return render_template('admin/login.html')

@app.route('/admin/panel')
@login_required
def admin_panel():
    try:
        return render_template('admin/panel.html', productos=productos)
    except Exception as e:
        app.logger.error(f'Error en el panel de administración: {str(e)}')
        flash('Error al cargar el panel de administración')
        return redirect(url_for('index'))

@app.route('/admin/agregar_producto', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    try:
        if request.method == 'POST':
            nuevo_producto = {
                'id': len(productos) + 1,
                'nombre': request.form['nombre'],
                'precio': float(request.form['precio']),
                'categoria': request.form['categoria'],
                'imagen': request.form['imagen'],
                'link': request.form['link']
            }
            
            productos.append(nuevo_producto)
            
            # Crear backup después de agregar un producto
            create_backup()
            
            # Limpiar caché relacionada con productos
            for key in list(cache.keys()):
                if key.startswith('index_') or key.startswith('productos_ajax_'):
                    del cache[key]
            
            flash('Producto agregado exitosamente')
            return redirect(url_for('admin_panel'))
        
        return render_template('admin/agregar_producto.html')
    except Exception as e:
        app.logger.error(f'Error al agregar producto: {str(e)}')
        flash('Error al agregar el producto')
        return redirect(url_for('admin_panel'))

@app.route('/admin/editar_producto/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    try:
        producto = next((p for p in productos if p['id'] == id), None)
        
        if not producto:
            flash('Producto no encontrado')
            return redirect(url_for('admin_panel'))
        
        if request.method == 'POST':
            producto['nombre'] = request.form['nombre']
            producto['precio'] = float(request.form['precio'])
            producto['categoria'] = request.form['categoria']
            producto['imagen'] = request.form['imagen']
            producto['link'] = request.form['link']
            
            # Crear backup después de editar un producto
            create_backup()
            
            # Limpiar caché relacionada con productos
            for key in list(cache.keys()):
                if key.startswith('index_') or key.startswith('productos_ajax_'):
                    del cache[key]
            
            flash('Producto actualizado exitosamente')
            return redirect(url_for('admin_panel'))
        
        return render_template('admin/editar_producto.html', producto=producto)
    except Exception as e:
        app.logger.error(f'Error al editar producto: {str(e)}')
        flash('Error al editar el producto')
        return redirect(url_for('admin_panel'))

@app.route('/admin/eliminar_producto/<int:id>')
@login_required
def eliminar_producto(id):
    try:
        global productos
        productos = [p for p in productos if p['id'] != id]
        
        # Crear backup después de eliminar un producto
        create_backup()
        
        # Limpiar caché relacionada con productos
        for key in list(cache.keys()):
            if key.startswith('index_') or key.startswith('productos_ajax_'):
                del cache[key]
        
        flash('Producto eliminado exitosamente')
        return redirect(url_for('admin_panel'))
    except Exception as e:
        app.logger.error(f'Error al eliminar producto: {str(e)}')
        flash('Error al eliminar el producto')
        return redirect(url_for('admin_panel'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Sesión cerrada exitosamente')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
