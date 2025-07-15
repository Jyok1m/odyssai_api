from flask import Blueprint, jsonify, render_template

# Create blueprint for welcome routes
welcome_bp = Blueprint("welcome", __name__)

@welcome_bp.route("/", methods=["GET"])
def welcome():
    """Welcome route for Odyssai API"""
    return render_template('welcome.html')

@welcome_bp.route("/health", methods=["GET"])
def health_check():
    """API health check route"""
    return jsonify({
        "status": "healthy",
        "message": "Odyssai API is running correctly",
        "service": "Odyssai Audio Transcription API"
    })
