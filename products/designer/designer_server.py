#!/usr/bin/env python3
"""
Interior Designer Flask Server
A REST API server that exposes the interior design functionality via HTTP endpoints
"""

import os
import sys
import traceback
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import tempfile

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from designer.image_analyzer import ImageAnalyzer
from designer.design_critic import DesignCritic
from designer.input_parser import InputParser
from designer.product_finder import ProductFinder

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def load_api_keys():
    """Load API keys from .env file"""
    # Look for .env file in parent directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(env_path)
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    serpapi_key = os.getenv('SERPAPI_API_KEY')
    
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    if not serpapi_key:
        raise ValueError("SERPAPI_API_KEY not found in .env file")
    
    return gemini_key, serpapi_key

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize AI components globally
try:
    gemini_key, serpapi_key = load_api_keys()
    image_analyzer = ImageAnalyzer(gemini_key)
    design_critic = DesignCritic(gemini_key)
    input_parser = InputParser(gemini_key)
    product_finder = ProductFinder(gemini_key, serpapi_key)
except Exception as e:
    print(f"Failed to initialize AI components: {e}")
    sys.exit(1)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'interior-designer-api'})

@app.route('/analyze', methods=['POST'])
def analyze_room():
    """
    Main endpoint for complete room analysis
    Expects: multipart/form-data with 'image' file and 'preferences' text
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Check if preferences are provided
        preferences = request.form.get('preferences')
        if not preferences:
            return jsonify({'error': 'No preferences provided'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        try:
            # Step 1: Analyze Image
            room_analysis = image_analyzer.analyze_room_image(temp_path)
            if not room_analysis:
                return jsonify({'error': 'Failed to analyze image'}), 500
            
            # Step 2: Design Critique
            design_critique = design_critic.critique_design(room_analysis)
            if not design_critique:
                return jsonify({'error': 'Failed to generate design critique'}), 500
            
            # Step 3: Parse User Input
            user_preferences = input_parser.parse_user_input(preferences)
            if not user_preferences or not user_preferences.get('parsed_successfully'):
                return jsonify({'error': 'Failed to parse user preferences'}), 400
            
            # Step 4: Generate Product Recommendations
            products = product_finder.generate_product_recommendations(
                room_analysis, design_critique, user_preferences
            )
            
            if not products:
                return jsonify({'error': 'No product recommendations found'}), 404
            
            # Format response
            response = {
                'success': True,
                'room_analysis': room_analysis,
                'design_critique': design_critique,
                'user_preferences': user_preferences,
                'product_recommendations': products,
                'summary': {
                    'room_type': room_analysis.get('room_type', 'Unknown'),
                    'current_style': room_analysis.get('current_style', 'Unknown'),
                    'budget': user_preferences.get('budget_amount', 0),
                    'num_recommendations': len(products)
                }
            }
            
            return jsonify(response)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/analyze/step1', methods=['POST'])
def analyze_image_only():
    """
    Step 1 only: Analyze room image
    Expects: multipart/form-data with 'image' file
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        try:
            room_analysis = image_analyzer.analyze_room_image(temp_path)
            if not room_analysis:
                return jsonify({'error': 'Failed to analyze image'}), 500
            
            return jsonify({
                'success': True,
                'room_analysis': room_analysis
            })
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/analyze/step2', methods=['POST'])
def critique_design():
    """
    Step 2: Design critique based on room analysis
    Expects: JSON with 'room_analysis' data
    """
    try:
        data = request.get_json()
        if not data or 'room_analysis' not in data:
            return jsonify({'error': 'No room analysis data provided'}), 400
        
        design_critique = design_critic.critique_design(data['room_analysis'])
        if not design_critique:
            return jsonify({'error': 'Failed to generate design critique'}), 500
        
        return jsonify({
            'success': True,
            'design_critique': design_critique
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/analyze/step3', methods=['POST'])
def parse_preferences():
    """
    Step 3: Parse user preferences
    Expects: JSON with 'preferences' text
    """
    try:
        data = request.get_json()
        if not data or 'preferences' not in data:
            return jsonify({'error': 'No preferences provided'}), 400
        
        user_preferences = input_parser.parse_user_input(data['preferences'])
        if not user_preferences or not user_preferences.get('parsed_successfully'):
            return jsonify({'error': 'Failed to parse user preferences'}), 400
        
        return jsonify({
            'success': True,
            'user_preferences': user_preferences
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/analyze/step4', methods=['POST'])
def generate_recommendations():
    """
    Step 4: Generate product recommendations
    Expects: JSON with 'room_analysis', 'design_critique', 'user_preferences'
    """
    try:
        data = request.get_json()
        required_fields = ['room_analysis', 'design_critique', 'user_preferences']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        products = product_finder.generate_product_recommendations(
            data['room_analysis'], 
            data['design_critique'], 
            data['user_preferences']
        )
        
        if not products:
            return jsonify({'error': 'No product recommendations found'}), 404
        
        return jsonify({
            'success': True,
            'product_recommendations': products,
            'num_recommendations': len(products)
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    print("Starting Interior Designer API Server...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /analyze - Complete analysis (image + preferences)")
    print("  POST /analyze/step1 - Image analysis only")
    print("  POST /analyze/step2 - Design critique")
    print("  POST /analyze/step3 - Parse preferences") 
    print("  POST /analyze/step4 - Generate recommendations")
    print(f"Server running on http://localhost:8009")
    
    app.run(host='0.0.0.0', port=8009, debug=True)