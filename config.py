import os

class Config:
    # Veritabanı yapılandırması
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-SocketIO yapılandırması
    SECRET_KEY = os.urandom(24)
    
    # Uygulama yapılandırması
    MAX_MESSAGE_LENGTH = 1000
    MAX_ROOM_NAME_LENGTH = 100
    MAX_ROOM_DESCRIPTION_LENGTH = 500
