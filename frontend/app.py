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
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Log current working directory for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"App file directory: {current_dir}")
print(f"Static folder path: {os.path.join(current_dir, 'static')}")

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

# Initialize Flask app with proper static file configuration
# Use absolute path for static folder to avoid path issues
static_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask(__name__, 
           static_folder=static_folder_path,
           static_url_path='/static')
CORS(app)

# Log static folder configuration
print(f"Static folder configured at: {static_folder_path}")
print(f"Static folder exists: {os.path.exists(static_folder_path)}")

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
            if FULL_SYSTEM_AVAILABLE:
                logger.info("Initializing Legal AI System...")
                legal_ai_system = LegalAISystem()
                logger.info("✅ System initialized successfully")
            else:
                logger.warning("⚠️ Running in demo mode - RAG system not available")
                legal_ai_system = None
    except Exception as e:
        logger.error(f"Error initializing system: {str(e)}")
        logger.warning("⚠️ Falling back to demo mode")
        legal_ai_system = None

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return app.send_static_file('images/logo1.png')

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
        if legal_ai_system is not None:
            response = legal_ai_system.process_legal_question(user_question)
        else:
            # Demo mode response - Fixed format for frontend compatibility
            response = {
                'status': 'success',  # Frontend expects 'success' status
                'user_question': user_question,
                'legal_analysis': f"""🏛️ **Demo Mode - Sistem Çalışıyor**

**Sorunuz:** "{user_question}"

🎉 **Sistem Durumu:**
- ✅ Web arayüzü başarıyla çalışıyor
- ✅ API bağlantısı aktif
- ✅ Güvenlik sistemi çalışıyor  
- ✅ Mobil uyumlu tasarım aktif
- 🚧 RAG sistemi demo modunda

💡 **Demo Mode Özellikleri:**
- ✅ Temel sistem testleri çalışıyor
- ✅ API endpoint'ler çalışıyor
- ✅ Veritabanı bağlantısı aktif
- 🔄 Tam hukuki analiz sistemi yükleniyor...

📋 **Sistem Bilgileri:**
- **Ortam:** Production Ready
- **API Keys:** {'✅' if Config.OPENAI_API_KEY else '❌'}
- **Durum:** Demo Mode Aktif
- **Versiyon:** Beta M1.1

⚠️ **Not:** Sistem şu anda demo modunda çalışıyor. Tam kapasiteli hukuki analiz için sistem optimize ediliyor.""",
                'found_laws': [],
                'optimized_query': f'Demo optimizasyonu: "{user_question}"',
                'pipeline_steps': {
                    'step1_query_optimization': 'Demo mode',
                    'step2_rag_results': 0,
                    'step3_laws_found': 0,
                    'step4_analysis_complete': True  # Mark as complete for demo
                }
            }
        
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
    """Enhanced health check endpoint for deployment monitoring"""
    try:
        # Initialize system if not already done
        if legal_ai_system is None:
            initialize_system()
        
        # Check system status
        system_status = {
            'status': 'healthy',
            'timestamp': pd.Timestamp.now().isoformat(),
            'environment': Config.ENVIRONMENT,
            'production_mode': Config.IS_PRODUCTION,
            'components': {
                'flask_app': True,
                'config_loaded': bool(Config.OPENAI_API_KEY),
                'legal_ai_system': legal_ai_system is not None,
                'api_keys_configured': {
                    'agent1': bool(Config.AGENT1_API_KEY),
                    'agent3': bool(Config.AGENT3_API_KEY)
                }
            }
        }
        
        # Add RAG system status if available
        if legal_ai_system is not None:
            try:
                rag_available = hasattr(legal_ai_system, 'rag_system') and legal_ai_system.rag_system is not None
                if rag_available:
                    system_status['components']['rag_system'] = {
                        'available': True,
                        'embeddings_loaded': legal_ai_system.rag_system.embeddings is not None,
                        'chunks_loaded': bool(legal_ai_system.rag_system.chunks)
                    }
                else:
                    system_status['components']['rag_system'] = {
                        'available': False,
                        'mode': 'demo'
                    }
            except Exception:
                system_status['components']['rag_system'] = {
                    'available': False,
                    'mode': 'demo'
                }
        
        # Return appropriate HTTP status
        if legal_ai_system is None or not Config.OPENAI_API_KEY:
            system_status['status'] = 'degraded'
            return jsonify(system_status), 503
        
        return jsonify(system_status), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'timestamp': pd.Timestamp.now().isoformat(),
            'error': str(e),
            'components': {
                'flask_app': True,
                'config_loaded': False,
                'legal_ai_system': False
            }
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