from flask import Flask
import socketio

sio = socketio.Server()
app = Flask(__name__)
app.secret_key = '123'

from app import routes
