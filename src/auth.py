import email
import json
from click import password_option
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.constants import http_status_codes 
from src.database import User, db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flasgger import swag_from

auth = Blueprint(name="auth", import_name=__name__, url_prefix="/api/v1/auth")

@auth.post('/register')
@swag_from('./docs/auth/register.yaml')
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

@auth.post('/login')
@swag_from('./docs/auth/login.yaml')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')    

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'username': user.username,
                    'email': user.email
                }
            }), http_status_codes.HTTP_200_OK

    return jsonify({'error': 'Wrong credentials'}), http_status_codes.HTTP_401_UNAUTHORIZED


# ONLY SEND IF WE GET THE REQUEST WITH ACCESS TOKENS 
@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    
    user = User.query.filter_by(id=user_id).first()
    
    if user:
        return jsonify({
            'user': {
                'username': user.username, 
                'email': user.email
            }
        }), http_status_codes.HTTP_200_OK
    
    return jsonify({'error': 'Could not understand request. Check your authentication token'}), http_status_codes.HTTP_400_BAD_REQUEST


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_user_token():
    #TODO: not working propelly
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)

    return json({
        'access': access_token
    }), http_status_codes.HTTP_200_OK
