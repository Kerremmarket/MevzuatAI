"""
Flask Web Frontend for Legal AI System
Simple ChatGPT-like interface
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
import logging
import numpy as np
import pandas as pd
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import LegalAISystem
    FULL_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Full system not available: {e}")
    FULL_SYSTEM_AVAILABLE = False
    LegalAISystem = None
from config.config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variable to hold the AI system
legal_ai_system = None

def convert_to_json_serializable(obj):
    """Convert numpy/pandas types to JSON serializable types"""
    if isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, pd.Int64Dtype)):
        return int(obj)
    elif isinstance(obj, (np.floating, pd.Float64Dtype)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj

def initialize_system():
    """Initialize the Legal AI System"""
    global legal_ai_system
    try:
        if legal_ai_system is None:
            logger.info("Initializing Legal AI System...")
            legal_ai_system = LegalAISystem()
            logger.info("✅ System initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing system: {str(e)}")
        raise

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """API endpoint to process legal questions"""
    try:
        data = request.get_json()
        user_question = data.get('question', '').strip()
        
        if not user_question:
            return jsonify({
                'status': 'error',
                'message': 'Lütfen bir soru yazın'
            }), 400
        
        # Ensure system is initialized
        if legal_ai_system is None:
            initialize_system()
        
        # Process the question
        response = legal_ai_system.process_legal_question(user_question)
        
        # Convert numpy/pandas types to JSON serializable types
        clean_response = convert_to_json_serializable(response)
        
        return jsonify({
            'status': 'success',
            'response': clean_response
        })
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Sistem hatası: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        if legal_ai_system is None:
            return jsonify({
                'status': 'not_ready',
                'message': 'System not initialized'
            })
        
        return jsonify({
            'status': 'ready',
            'message': 'Legal AI System is ready'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    try:
        # Initialize system on startup
        initialize_system()
        
        # Log environment info
        logger.info(f"🌍 Environment: {Config.ENVIRONMENT}")
        logger.info(f"🔧 Production Mode: {Config.IS_PRODUCTION}")
        logger.info(f"🌐 Host: {Config.FLASK_HOST}:{Config.FLASK_PORT}")
        
        # Run Flask app
        app.run(
            host=Config.FLASK_HOST,
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG
        )
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        print(f"❌ Error: {str(e)}")
        print("Make sure your OpenAI API key is set and all dependencies are installed.")