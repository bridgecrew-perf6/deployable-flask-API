from flask import Flask

app = Flask(__name__)

#Creating basic route

@app.get('/')
def index():
    return 'hello world'
