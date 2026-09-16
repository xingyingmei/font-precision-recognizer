"""
Flask Application for Font Precision Recognizer
Main entry point for the web application
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from src.font_recognizer import FontRecognizer
from src.font_searcher import FontSearcher

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_IMAGE_SIZE', 10485760))

# Enable CORS
CORS(app)

# Initialize services
recognizer = FontRecognizer()
searcher = FontSearcher()


# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/recognize')
def recognize_page():
    """Font recognition page"""
    return render_template('recognize.html')


@app.route('/search')
def search_page():
    """Font search page"""
    return render_template('search.html')


# ============================================================================
# API Routes - Recognition
# ============================================================================

@app.route('/api/recognize-font', methods=['POST'])
def recognize_font():
    """
    Recognize fonts from an uploaded image
    
    Expected request:
    - File upload with key 'image'
    
    Returns:
    - JSON with recognized fonts and sources
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            file.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Recognize fonts
            results = recognizer.recognize_from_image(temp_path)
            
            return jsonify({
                'status': 'success',
                'fonts': results
            })
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        logger.error(f"Recognition error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recognize-font-base64', methods=['POST'])
def recognize_font_base64():
    """
    Recognize fonts from base64 encoded image
    
    Expected request:
    {
        "image": "base64_encoded_image_data"
    }
    
    Returns:
    - JSON with recognized fonts and sources
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        import base64
        import tempfile
        
        # Decode base64 image
        image_data = data['image']
        if image_data.startswith('data:image/'):
            image_data = image_data.split(',')[1]
        
        # Save to temporary file
        image_bytes = base64.b64decode(image_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp.write(image_bytes)
            temp_path = tmp.name
        
        try:
            # Recognize fonts
            results = recognizer.recognize_from_image(temp_path)
            
            return jsonify({
                'status': 'success',
                'fonts': results
            })
        
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        logger.error(f"Base64 recognition error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API Routes - Search
# ============================================================================

@app.route('/api/search-font', methods=['GET'])
def search_font():
    """
    Search for fonts by name
    
    Query parameters:
    - query (required): Font name or description
    - type (optional): Font type (serif, sans-serif, script, etc.)
    - license (optional): License type (free, commercial, subscription)
    - max_results (optional): Maximum number of results (default: 50)
    
    Returns:
    - JSON with search results and source links
    """
    try:
        query = request.args.get('query', '')
        font_type = request.args.get('type')
        license_type = request.args.get('license')
        max_results = int(request.args.get('max_results', 50))
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Perform search
        results = searcher.search(query, font_type, license_type, max_results)
        
        return jsonify({
            'status': 'success',
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/bulk-search', methods=['POST'])
def bulk_search():
    """
    Search for multiple fonts at once
    
    Expected request:
    {
        "fonts": ["Font 1", "Font 2", "Font 3"]
    }
    
    Returns:
    - JSON with results for each font
    """
    try:
        data = request.get_json()
        
        if not data or 'fonts' not in data:
            return jsonify({'error': 'No fonts provided'}), 400
        
        fonts = data['fonts']
        
        if not isinstance(fonts, list):
            return jsonify({'error': 'Fonts must be a list'}), 400
        
        # Perform bulk search
        results = searcher.bulk_search(fonts)
        
        return jsonify({
            'status': 'success',
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Bulk search error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API Routes - Sources
# ============================================================================

@app.route('/api/sources', methods=['GET'])
def get_sources():
    """
    Get all available font sources
    
    Returns:
    - JSON list of all font sources with URLs
    """
    try:
        sources = searcher.get_sources()
        
        return jsonify({
            'status': 'success',
            'total': len(sources),
            'sources': sources
        })
    
    except Exception as e:
        logger.error(f"Error fetching sources: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API Routes - Database
# ============================================================================

@app.route('/api/font-details/<font_name>', methods=['GET'])
def get_font_details(font_name):
    """
    Get detailed information about a specific font
    
    Parameters:
    - font_name: Name of the font
    
    Returns:
    - JSON with font details
    """
    try:
        details = searcher.get_font_details(font_name)
        
        if details:
            return jsonify({
                'status': 'success',
                'font': details
            })
        else:
            return jsonify({
                'status': 'not_found',
                'message': f'Font "{font_name}" not found in database'
            }), 404
    
    except Exception as e:
        logger.error(f"Error fetching font details: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/filter-fonts', methods=['POST'])
def filter_fonts():
    """
    Filter fonts based on criteria
    
    Expected request:
    {
        "criteria": {
            "name": "Arial",
            "type": "sans-serif",
            "license": "free"
        }
    }
    
    Returns:
    - JSON with filtered fonts
    """
    try:
        data = request.get_json()
        
        if not data or 'criteria' not in data:
            return jsonify({'error': 'No filter criteria provided'}), 400
        
        criteria = data['criteria']
        results = searcher.filter_fonts(criteria)
        
        return jsonify({
            'status': 'success',
            'results': results,
            'count': len(results)
        })
    
    except Exception as e:
        logger.error(f"Filter error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Health Check
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Font Precision Recognizer',
        'version': '1.0.0'
    })


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 10MB'}), 413


# ============================================================================
# CLI Commands
# ============================================================================

@app.shell_context_processor
def make_shell_context():
    """Shell context processor for Flask CLI"""
    return {
        'recognizer': recognizer,
        'searcher': searcher
    }


if __name__ == '__main__':
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Starting Font Precision Recognizer on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
