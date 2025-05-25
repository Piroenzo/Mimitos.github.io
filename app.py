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
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'mimitos.balanceados@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'lakj dbwp gkdq msbk')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'mimitos.balanceados@gmail.com')
app.config['ADMIN_PASSWORD'] = 'mimitos2024'

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
        "imagen": "static/img/Dog_Selection_adulto_x21k.jpeg",
        "precio": 45000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Dog%20Selection%20Adulto%2021KG"
    },
    {
        "id": 2,
        "nombre": "Dog Selection Cachorro 21KG",
        "imagen": "static/img/Dog_election_cachorro_x21k.jpeg",
        "precio": 48000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Dog%20Selection%20Cachorro%2021KG"
    },
    {
        "id": 3,
        "nombre": "Dog Selection Adulto RP 15KG",
        "imagen": "static/img/Dog_Selection_ad_RP_x15k .jpeg",
        "precio": 35000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Dog%20Selection%20Adulto%20RP%2015KG"
    },
    {
        "id": 4,
        "nombre": "Cat Selection 10KG",
        "imagen": "static/img/Cat_Selection_x10k.jpeg",
        "precio": 28000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Cat%20Selection%2010KG"
    },
    {
        "id": 5,
        "nombre": "Excellent Gato Adulto 7.5KG",
        "imagen": "static/img/Excellent_gato_x7.5k.jpeg",
        "precio": 32000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Excellent%20Gato%20Adulto%207.5KG"
    },
    {
        "id": 6,
        "nombre": "Excellent Gato Urinario 7.5KG",
        "imagen": "static/img/Excellent_urinary_x7.5k.jpeg",
        "precio": 35000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Excellent%20Gato%20Urinario%207.5KG"
    },
    {
        "id": 7,
        "nombre": "Excellent Gato Adulto 15KG",
        "imagen": "static/img/Excellent_gato_x15k .jpeg",
        "precio": 58000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Excellent%20Gato%20Adulto%2015KG"
    },
    {
        "id": 8,
        "nombre": "Cat Chow Gatito 8KG",
        "imagen": "static/img/Cat_chow_gatito_x8k .jpeg",
        "precio": 25000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Cat%20Chow%20Gatito%208KG"
    },
    {
        "id": 9,
        "nombre": "Cat Chow Gatito 15KG",
        "imagen": "static/img/Cat_chow_gatito_x15k.jpeg",
        "precio": 42000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Cat%20Chow%20Gatito%2015KG"
    },
    {
        "id": 10,
        "nombre": "Cat Chow Adulto 8KG",
        "imagen": "static/img/Cat_chow_adulto_x8k.jpeg",
        "precio": 23000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Cat%20Chow%20Adulto%208KG"
    },
    {
        "id": 11,
        "nombre": "Cat Chow Adulto 15KG",
        "imagen": "static/img/Cat_chow_adulto_x15k .jpeg",
        "precio": 40000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Cat%20Chow%20Adulto%2015KG"
    },
    {
        "id": 12,
        "nombre": "Dog Chow Cachorro 21KG",
        "imagen": "static/img/Dog_chow_cachorro_x21k.jpeg",
        "precio": 42000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Dog%20Chow%20Cachorro%2021KG"
    },
    {
        "id": 13,
        "nombre": "Dog Chow Adulto 21KG",
        "imagen": "static/img/Dog_chow_adultox21k.jpeg",
        "precio": 38000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Dog%20Chow%20Adulto%2021KG"
    },
    {
        "id": 14,
        "nombre": "Chacal 22KG",
        "imagen": "static/img/Chacal_x22k.jpeg",
        "precio": 35000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Chacal%2022KG"
    },
    {
        "id": 15,
        "nombre": "Tiernitos Adulto 21KG",
        "imagen": "static/img/Tiernitos_adultox21k.jpeg",
        "precio": 32000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Tiernitos%20Adulto%2021KG"
    },
    {
        "id": 16,
        "nombre": "Pachá 22KG",
        "imagen": "static/img/Pachá_x22k.jpeg",
        "precio": 33000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Pachá%2022KG"
    },
    {
        "id": 17,
        "nombre": "Maxi Adulto 15KG",
        "imagen": "static/img/Maxi_adulto_x15k.jpeg",
        "precio": 28000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Maxi%20Adulto%2015KG"
    },
    {
        "id": 18,
        "nombre": "Sabrositos Gato Pescado 11KG",
        "imagen": "static/img/Sabrositos_gato_pescado_x11k.jpg",
        "precio": 32000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Sabrositos%20Gato%20Pescado%2011KG"
    },
    {
        "id": 19,
        "nombre": "Sabrositos Cachorro 8KG",
        "imagen": "static/img/Sabrositos_cachorro_x8k.jpg",
        "precio": 28000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Sabrositos%20Cachorro%208KG"
    },
    {
        "id": 20,
        "nombre": "Sabrositos Cachorro 18KG",
        "imagen": "static/img/Sabrositos_cachorro_x18k.jpg",
        "precio": 45000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Sabrositos%20Cachorro%2018KG"
    },
    {
        "id": 21,
        "nombre": "Sabrositos Gato 20KG",
        "imagen": "static/img/Sabrositos_gato_x20k.jpg",
        "precio": 55000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Sabrositos%20Gato%2020KG"
    },
    {
        "id": 22,
        "nombre": "Sabrositos Gato 10KG",
        "imagen": "static/img/Sabrositos_gato_x10k.jpg",
        "precio": 30000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Sabrositos%20Gato%2010KG"
    },
    {
        "id": 23,
        "nombre": "Sabrositos Adulto 15KG",
        "imagen": "static/img/Sabrosito_adulto_x15k.jpg",
        "precio": 35000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Sabrositos%20Adulto%2015KG"
    },
    {
        "id": 24,
        "nombre": "Sabrositos Adulto 22KG",
        "imagen": "static/img/Sabrositos_adulto_x22k.jpg",
        "precio": 48000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Sabrositos%20Adulto%2022KG"
    },
    {
        "id": 25,
        "nombre": "Biomax Cachorro 15KG",
        "imagen": "static/img/Biomax_Cach_x15kg.jpg",
        "precio": 42000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Biomax%20Cachorro%2015KG"
    },
    {
        "id": 26,
        "nombre": "Biomax Adulto RP 15KG",
        "imagen": "static/img/Biomax_Adulto_Rp_x15kg.jpg",
        "precio": 38000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Biomax%20Adulto%20RP%2015KG"
    },
    {
        "id": 27,
        "nombre": "Biomax Adulto 20KG",
        "imagen": "static/img/Biomax_Adulto_x20kg.jpg",
        "precio": 45000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Biomax%20Adulto%2020KG"
    },
    {
        "id": 28,
        "nombre": "Bred Dog Adulto 20KG",
        "imagen": "static/img/Bred_Dog_Adulto_x20kg.jpg",
        "precio": 42000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Bred%20Dog%20Adulto%2020KG"
    },
    {
        "id": 29,
        "nombre": "Old Prince Cordero Adulto/Cachorro 15KG",
        "imagen": "static/img/Old_Prince_Cordero_Adulto_Cach_x15kg.jpg",
        "precio": 55000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Old%20Prince%20Cordero%20Adulto/Cachorro%2015KG"
    },
    {
        "id": 30,
        "nombre": "Old Prince Cordero Adulto RP 15KG",
        "imagen": "static/img/Old_Prince_Cordero_Adulto_Rp_x15kg.jpg",
        "precio": 52000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Old%20Prince%20Cordero%20Adulto%20RP%2015KG"
    },
    {
        "id": 31,
        "nombre": "Old Prince Cordero Adulto 15KG",
        "imagen": "static/img/Old_Prince_Cordero_Adulto_x15kg.jpg",
        "precio": 55000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Old%20Prince%20Cordero%20Adulto%2015KG"
    },
    {
        "id": 32,
        "nombre": "Old Prince Tradicional 20KG",
        "imagen": "static/img/Old_Prince_Tradicional_x20kg.jpg",
        "precio": 48000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Old%20Prince%20Tradicional%2020KG"
    },
    {
        "id": 33,
        "nombre": "Mantenaince 22KG",
        "imagen": "static/img/Mantenaince_x22kg.jpg",
        "precio": 42000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Mantenaince%2022KG"
    },
    {
        "id": 34,
        "nombre": "Kitten 7.5KG",
        "imagen": "static/img/Kitten_x7,5k.jpg",
        "precio": 28000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Kitten%207.5KG"
    },
    {
        "id": 35,
        "nombre": "Urinary Care 7.5KG",
        "imagen": "static/img/URINARY_CARE x7,5k.jpg",
        "precio": 32000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Urinary%20Care%207.5KG"
    },
    {
        "id": 36,
        "nombre": "Urinary S-O 7.5KG",
        "imagen": "static/img/URINARY_S-O_x7,5k.jpg",
        "precio": 32000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Urinary%20S-O%207.5KG"
    },
    {
        "id": 37,
        "nombre": "Urinary Perro 10KG",
        "imagen": "static/img/URINARY_perro_10k.jpg",
        "precio": 38000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Urinary%20Perro%2010KG"
    },
    {
        "id": 38,
        "nombre": "Mini Puppy 15KG",
        "imagen": "static/img/Mini_puppy_x15k.jpg",
        "precio": 45000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Mini%20Puppy%2015KG"
    },
    {
        "id": 39,
        "nombre": "Mini Puppy 7.5KG",
        "imagen": "static/img/Mini_puppy_x7.5k.jpg",
        "precio": 28000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Mini%20Puppy%207.5KG"
    },
    {
        "id": 40,
        "nombre": "Mini Adulto 7.5KG",
        "imagen": "static/img/Mini_adulto_x7.5k.jpg",
        "precio": 26000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Mini%20Adulto%207.5KG"
    },
    {
        "id": 41,
        "nombre": "Fit 32 15KG",
        "imagen": "static/img/FIT_32_x15k.jpg",
        "precio": 42000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Fit%2032%2015KG"
    },
    {
        "id": 42,
        "nombre": "Fit 32 7.5KG",
        "imagen": "static/img/FIT_32_x7,5k .jpg",
        "precio": 28000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Fit%2032%207.5KG"
    },
    {
        "id": 43,
        "nombre": "Performance Gato 7.5KG",
        "imagen": "static/img/Perf._Gato_x7,5k.jpg",
        "precio": 30000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Performance%20Gato%207.5KG"
    },
    {
        "id": 44,
        "nombre": "Performance Kitten 7.5KG",
        "imagen": "static/img/Perf._Kitten_x7,5k.jpg",
        "precio": 32000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Performance%20Kitten%207.5KG"
    },
    {
        "id": 45,
        "nombre": "Performance Junior 15KG",
        "imagen": "static/img/Performance_junior_x15k.jpg",
        "precio": 45000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Performance%20Junior%2015KG"
    },
    {
        "id": 46,
        "nombre": "Performance Adulto 15KG",
        "imagen": "static/img/Performance_adulto_x15k.jpg",
        "precio": 42000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Performance%20Adulto%2015KG"
    },
    {
        "id": 47,
        "nombre": "Performance Adulto 20KG",
        "imagen": "static/img/Performance_adultox20k.jpg",
        "precio": 48000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Performance%20Adulto%2020KG"
    },
    {
        "id": 48,
        "nombre": "Medium Puppy 15KG",
        "imagen": "static/img/Medium_puppy_x15k.jpg",
        "precio": 45000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Medium%20Puppy%2015KG"
    },
    {
        "id": 49,
        "nombre": "Medium Adulto 15KG",
        "imagen": "static/img/Medium_adulto_x15k.jpg",
        "precio": 42000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Medium%20Adulto%2015KG"
    },
    {
        "id": 50,
        "nombre": "Infinity Cachorro 10KG",
        "imagen": "static/img/Infinity_cachorrro_x10k.jpg",
        "precio": 35000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Infinity%20Cachorro%2010KG"
    },
    {
        "id": 51,
        "nombre": "Infinity RP 15KG",
        "imagen": "static/img/Infinity_RP x15k.jpg",
        "precio": 42000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Infinity%20RP%2015KG"
    },
    {
        "id": 52,
        "nombre": "Infinity Adulto 21KG",
        "imagen": "static/img/Infinity_adulto_x21k.jpg",
        "precio": 55000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Infinity%20Adulto%2021KG"
    },
    {
        "id": 53,
        "nombre": "Infinity Gato 10KG",
        "imagen": "static/img/Infinity_gato_x10k.jpg",
        "precio": 35000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Infinity%20Gato%2010KG"
    },
    {
        "id": 54,
        "nombre": "Ultra Gato 10KG",
        "imagen": "static/img/Ultra_gato_x10.jpg",
        "precio": 38000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Ultra%20Gato%2010KG"
    },
    {
        "id": 55,
        "nombre": "Ultra Cachorro 10KG",
        "imagen": "static/img/Ultra_cach_x10.jpg",
        "precio": 40000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Ultra%20Cachorro%2010KG"
    },
    {
        "id": 56,
        "nombre": "Ultra Adulto 15KG",
        "imagen": "static/img/Ultra_adulto_15k.jpg",
        "precio": 45000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Ultra%20Adulto%2015KG"
    },
    {
        "id": 57,
        "nombre": "Nutricare Gato 7.5KG",
        "imagen": "static/img/Nutricare_gato_x7,5.jpg",
        "precio": 32000,
        "categoria": "gatos",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Nutricare%20Gato%207.5KG"
    },
    {
        "id": 58,
        "nombre": "Nutricare 20KG",
        "imagen": "static/img/Nutricare x20k.jpg",
        "precio": 48000,
        "categoria": "perros",
        "link": "https://wa.me/5492323534156?text=Hola,%20quiero%20consultar%20por%20el%20producto%20Nutricare%2020KG"
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
        page = request.args.get('page', 1, type=int)
        busqueda = request.args.get('q', '')
        per_page = 12

        # Intentar obtener datos del caché
        cache_key = f'index_{page}_{busqueda}'
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            return render_template('index.html', 
                                 productos=cached_data['productos'],
                                 current_page=page,
                                 total_pages=cached_data['total_pages'],
                                 busqueda=busqueda)

        # Si no hay caché, calcular los datos
        if busqueda:
            productos_filtrados = [p for p in productos if busqueda.lower() in p['nombre'].lower()]
        else:
            productos_filtrados = productos

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        productos_pagina = productos_filtrados[start_idx:end_idx]
        total_pages = ceil(len(productos_filtrados) / per_page)

        # Guardar en caché
        cache_data = {
            'productos': productos_pagina,
            'total_pages': total_pages
        }
        set_cached_data(cache_key, cache_data)

        return render_template('index.html',
                             productos=productos_pagina,
                             current_page=page,
                             total_pages=total_pages,
                             busqueda=busqueda)
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
                             current_page=page,
                             total_pages=total_pages,
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
                             current_page=page,
                             total_pages=total_pages,
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
                                   current_page=page,
                                   total_pages=total_pages)
        
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
                                   current_page=page,
                                   total_pages=total_pages,
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
