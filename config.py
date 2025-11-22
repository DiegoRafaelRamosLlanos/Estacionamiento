import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de impresora térmica
    PRINTER_ENABLED = True
    PRINTER_TYPE = 'network'
    PRINTER_IP = '192.168.18.43'  # IP configurada en la impresora
    PRINTER_PORT = 9100
    PRINTER_TIMEOUT = 5