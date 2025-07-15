import os
import tempfile
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.blob_loaders import FileSystemBlobLoader

# Charger les variables d'environnement
load_dotenv(find_dotenv())

parser_bp = Blueprint("parser", __name__)

# Extensions de fichiers autorisées
ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'wav', 'mp4', 'mpeg', 'mpga', 'webm'}

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@parser_bp.route("/", methods=["POST"])
def parse_audio():
    try:
        # Vérifier qu'un fichier a été envoyé
        if 'audio_file' not in request.files:
            return jsonify({
                "message": "Aucun fichier audio fourni",
                "status": "error"
            }), 400
        
        file = request.files['audio_file']
        
        # Vérifier que le fichier n'est pas vide
        if file.filename == '':
            return jsonify({
                "message": "Aucun fichier sélectionné",
                "status": "error"
            }), 400
        
        # Vérifier l'extension du fichier
        if not allowed_file(file.filename):
            return jsonify({
                "message": f"Extension de fichier non supportée. Extensions autorisées: {', '.join(ALLOWED_EXTENSIONS)}",
                "status": "error"
            }), 400
        
        # Récupérer la clé API OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({
                "message": "Clé API OpenAI manquante",
                "status": "error"
            }), 500
        
        print(f"Clé API OpenAI: {api_key}")

        # Sauvegarder temporairement le fichier
        filename = secure_filename(file.filename or "audio_file")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / filename
            file.save(temp_path)
            
            # Initialiser le parser OpenAI Whisper
            parser = OpenAIWhisperParser(
                api_key=api_key,
                language="fr",  # Langue française par défaut
                response_format="text",
                model="whisper-1"
            )

            # Créer le blob loader et le generic loader
            blob_loader = FileSystemBlobLoader(temp_path)
            loader = GenericLoader(blob_loader, parser)
            
            # Charger et traiter l'audio
            docs = loader.load()
            
            if not docs:
                return jsonify({
                    "message": "La transcription est vide. Vérifiez que l'audio contient de la voix exploitable.",
                    "status": "error"
                }), 422

            # Extraire la transcription
            transcription = ""
            for doc in docs:
                transcription += doc.page_content
                print(doc.page_content)  # Afficher la transcription pour le débogage
            
            return jsonify({
                "message": "Audio transcrit avec succès",
                "status": "success",
                "data": {
                    "transcription": transcription.strip(),
                    "filename": filename
                }
            })
    
    except Exception as e:
        return jsonify({
            "message": f"Erreur lors de la transcription: {str(e)}",
            "status": "error"
        }), 500
