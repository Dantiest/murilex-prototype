from flask import Flask
from flask_session import Session
from routes.auth import auth_bp
from routes.details import details_bp
from routes.main import main_bp
from routes.watchman import watchman_bp
from sockets import socketio

app = Flask(__name__)
app.secret_key = 'abecedarulputernic'

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Initialize Flask-Session
Session(app)

socketio.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(details_bp)
app.register_blueprint(main_bp)
app.register_blueprint(watchman_bp)

if __name__ == '__main__':
    socketio.run(app, debug=True)