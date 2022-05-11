from flask import Blueprint

auth = Blueprint(name="auth", import_name=__name__, url_prefix="/api/v1/auth")

@auth.post('/register')
def register():
    return "User created"

@auth.get('/me')
def me():
    return "user: me"