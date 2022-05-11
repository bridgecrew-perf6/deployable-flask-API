from flask import Flask, jsonify

app = Flask(__name__)

#Creating basic route

@app.get('/')
def index():
    return jsonify({"message": "hello world"})
