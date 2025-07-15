from flask import Flask
from flask_cors import CORS
from app.routes.hello import hello_bp
from app.routes.parser import parser_bp

def create_app():
    app = Flask(__name__)

    CORS(app)
    
    app.register_blueprint(hello_bp, url_prefix="/")
    app.register_blueprint(parser_bp, url_prefix="/parse")

    return app
