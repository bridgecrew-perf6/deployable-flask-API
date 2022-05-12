import email
from click import password_option
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.constants import http_status_codes 
from src.database import User, db

auth = Blueprint(name="auth", import_name=__name__, url_prefix="/api/v1/auth")

@auth.post('/register')
def register():
    
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    # BASIC VALIDATION
    if len(password) < 6:
        return jsonify({'error': 'Password to short'}), http_status_codes.HTTP_400_BAD_REQUEST
    
    if len(username) < 3:
        return jsonify({'error': 'Username to short'}), http_status_codes.HTTP_400_BAD_REQUEST
    
    if not username.isalnum() or ' ' in username:
        return jsonify({'error': '''Should be alphanumeric  and must not use spaces'''}), http_status_codes.HTTP_400_BAD_REQUEST

    if not validators.email(email):
       return jsonify({'error': 'Email not valid'}), http_status_codes.HTTP_400_BAD_REQUEST
    
    # CHECK UNIQUES
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email is taken'}), http_status_codes.HTTP_409_CONFLICT
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username is taken'}), http_status_codes.HTTP_409_CONFLICT
    
    # HASH PASSWORD
    pwd = generate_password_hash(password)

    # Create user
    user = User(username=username, password=pwd, email=email)
    db.session.add(user)
    db.session.commit() 

    return jsonify({
        'message': 'User created!',
        'user': {
            'username': username,
            'email': email
        }
    }), http_status_codes.HTTP_201_CREATED

    



@auth.get('/me')
def me():
    return jsonify( user = "me")