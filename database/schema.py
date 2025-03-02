from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

# Kullanıcı rolleri için enum değerleri
class UserRole:
    ADMIN = 'idare'
    TEACHER = 'öğretmen'
    STUDENT = 'öğrenci'

# Oda üyeliği tablosu (Many-to-Many ilişki için)
room_members = db.Table('room_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('room_id', db.Integer, db.ForeignKey('rooms.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), nullable=True) 
    full_name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    messages = db.relationship('Message', backref='author', lazy=True)
    rooms = db.relationship('Room', secondary=room_members, backref=db.backref('members', lazy='dynamic'))
    created_rooms = db.relationship('Room', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can_send_message(self, room):
        return self.role in [UserRole.ADMIN, UserRole.TEACHER]

    def can_read_message(self, room):
        return True  # Tüm roller okuyabilir

    def can_manage_rooms(self):
        return self.role == UserRole.ADMIN

    def can_manage_users(self):
        return self.role == UserRole.ADMIN
    
    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # İlişkiler
    messages = db.relationship('Message', backref='room', lazy=True)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255))  # Dosya yolu
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    is_system_message = db.Column(db.Boolean, default=False)  # Katılma/ayrılma bildirimleri için
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'room_id': self.room_id,
            'author': self.author.username,
            'is_system_message': self.is_system_message
        }
