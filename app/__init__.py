from flask import Flask
from flask_cors import CORS
from app.routes.parser import parser_bp
from app.routes.welcome import welcome_bp

def create_app():
    app = Flask(__name__)

    CORS(app)
    
    # Enregistrer les blueprints
    app.register_blueprint(welcome_bp)  # Route d'accueil à la racine
    app.register_blueprint(parser_bp, url_prefix="/parser")

    return app
