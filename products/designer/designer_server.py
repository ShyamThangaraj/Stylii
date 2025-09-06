#!/usr/bin/env python3
"""
Interior Designer Flask Server
A REST API server that exposes the interior design functionality via HTTP endpoints
"""

import os
import sys
import traceback
import logging
from flask import Flask, request, jsonify, Response, stream_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import tempfile
import json

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('designer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger.info("Importing designer modules...")
from designer.image_analyzer import ImageAnalyzer
from designer.design_critic import DesignCritic
from designer.input_parser import InputParser
from designer.product_finder import ProductFinder
logger.info("Designer modules imported successfully")

app = Flask(__name__)
logger.info("Flask application initialized")

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

logger.info(f"Configuration set - Upload folder: {UPLOAD_FOLDER}")
logger.info(f"Configuration set - Max file size: {MAX_CONTENT_LENGTH} bytes")
logger.info(f"Configuration set - Allowed extensions: {ALLOWED_EXTENSIONS}")

def load_api_keys():
    """Load API keys from .env file"""
    logger.info("Loading API keys from .env file...")
    # Look for .env file in parent directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    logger.debug(f"Looking for .env file at: {env_path}")
    load_dotenv(env_path)

    gemini_key = os.getenv('GEMINI_API_KEY')
    serpapi_key = os.getenv('SERPAPI_API_KEY')

    if not gemini_key:
        logger.error("GEMINI_API_KEY not found in .env file")
        raise ValueError("GEMINI_API_KEY not found in .env file")
    if not serpapi_key:
        logger.error("SERPAPI_API_KEY not found in .env file")
        raise ValueError("SERPAPI_API_KEY not found in .env file")

    logger.info("API keys loaded successfully")
    logger.debug(f"GEMINI_API_KEY: {'*' * (len(gemini_key) - 4) + gemini_key[-4:]}")
    logger.debug(f"SERPAPI_API_KEY: {'*' * (len(serpapi_key) - 4) + serpapi_key[-4:]}")
    return gemini_key, serpapi_key

def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    logger.debug(f"File extension check for '{filename}': {allowed}")
    return allowed

# Initialize AI components globally
logger.info("Initializing AI components...")
try:
    gemini_key, serpapi_key = load_api_keys()
    logger.info("Creating ImageAnalyzer instance...")
    image_analyzer = ImageAnalyzer(gemini_key)
    logger.info("Creating DesignCritic instance...")
    design_critic = DesignCritic(gemini_key)
    logger.info("Creating InputParser instance...")
    input_parser = InputParser(gemini_key)
    logger.info("Creating ProductFinder instance...")
    product_finder = ProductFinder(gemini_key, serpapi_key)
    logger.info("All AI components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AI components: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    print(f"Failed to initialize AI components: {e}")
    sys.exit(1)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return jsonify({'status': 'healthy', 'service': 'interior-designer-api'})

@app.route('/analyze-stream', methods=['POST'])
def analyze_room_stream():
    """
    Streaming endpoint for complete room analysis
    Expects: multipart/form-data with 'image' file and 'preferences' text
    Returns: Server-sent events with progressive updates
    """
    request_id = f"req_{int(__import__('time').time())}"
    logger.info(f"[{request_id}] Starting streaming room analysis request")

    # Process request data OUTSIDE the generator
    try:
        # Check if image file is present
        logger.debug(f"[{request_id}] Checking for image file in request")
        if 'image' not in request.files:
            logger.error(f"[{request_id}] No image file provided in request")
            return Response(f"data: {json.dumps({'error': 'No image file provided'})}\n\n", mimetype='text/plain')

        file = request.files['image']
        logger.info(f"[{request_id}] Image file found: {file.filename}")
        if file.filename == '':
            logger.error(f"[{request_id}] Empty filename provided")
            return Response(f"data: {json.dumps({'error': 'No image file selected'})}\n\n", mimetype='text/plain')

        # Check if preferences are provided
        preferences = request.form.get('preferences')
        logger.info(f"[{request_id}] Preferences received: {len(preferences) if preferences else 0} characters")
        if not preferences:
            logger.error(f"[{request_id}] No preferences provided")
            return Response(f"data: {json.dumps({'error': 'No preferences provided'})}\n\n", mimetype='text/plain')

        # Validate file type
        if not allowed_file(file.filename):
            allowed_extensions = ", ".join(ALLOWED_EXTENSIONS)
            logger.error(f"[{request_id}] Invalid file type for {file.filename}")
            return Response(f"data: {json.dumps({'error': f'Unsupported file type. Allowed: {allowed_extensions}'})}\n\n", mimetype='text/plain')

        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"[{request_id}] Saving file to temporary path: {temp_path}")
        file.save(temp_path)
        logger.info(f"[{request_id}] File saved successfully ({os.path.getsize(temp_path)} bytes)")

    except Exception as e:
        logger.error(f"[{request_id}] Request processing error: {str(e)}")
        logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
        return Response(f"data: {json.dumps({'error': f'Request processing error: {str(e)}'})}\n\n", mimetype='text/plain')

    def generate():
        try:
            # Step 1: Analyze Image
            logger.info(f"[{request_id}] Starting Step 1: Image Analysis")
            yield f"data: {json.dumps({'status': 'analyzing_image', 'step': 1, 'message': 'Analyzing room image...'})}\n\n"
            room_analysis = image_analyzer.analyze_room_image(temp_path)
            if not room_analysis:
                logger.error(f"[{request_id}] Failed to analyze image")
                yield f"data: {json.dumps({'error': 'Failed to analyze image'})}\n\n"
                return

            logger.info(f"[{request_id}] Image analysis completed successfully")
            logger.debug(f"[{request_id}] Room analysis result: {room_analysis}")
            yield f"data: {json.dumps({'status': 'image_analyzed', 'step': 1, 'room_analysis': room_analysis})}\n\n"

            # Step 2: Design Critique
            logger.info(f"[{request_id}] Starting Step 2: Design Critique")
            yield f"data: {json.dumps({'status': 'critiquing_design', 'step': 2, 'message': 'Generating design critique...'})}\n\n"
            design_critique = design_critic.critique_design(room_analysis)
            if not design_critique:
                logger.error(f"[{request_id}] Failed to generate design critique")
                yield f"data: {json.dumps({'error': 'Failed to generate design critique'})}\n\n"
                return

            logger.info(f"[{request_id}] Design critique completed successfully")
            logger.debug(f"[{request_id}] Design critique result: {design_critique}")
            yield f"data: {json.dumps({'status': 'design_critiqued', 'step': 2, 'design_critique': design_critique})}\n\n"

            # Step 3: Parse User Input
            logger.info(f"[{request_id}] Starting Step 3: Parse User Preferences")
            yield f"data: {json.dumps({'status': 'parsing_preferences', 'step': 3, 'message': 'Parsing user preferences...'})}\n\n"
            user_preferences = input_parser.parse_user_input(preferences)
            if not user_preferences or not user_preferences.get('parsed_successfully'):
                logger.error(f"[{request_id}] Failed to parse user preferences")
                yield f"data: {json.dumps({'error': 'Failed to parse user preferences'})}\n\n"
                return

            logger.info(f"[{request_id}] User preferences parsed successfully")
            logger.debug(f"[{request_id}] User preferences result: {user_preferences}")
            yield f"data: {json.dumps({'status': 'preferences_parsed', 'step': 3, 'user_preferences': user_preferences})}\n\n"

            # Step 4: Generate Product Recommendations
            logger.info(f"[{request_id}] Starting Step 4: Generate Product Recommendations")
            yield f"data: {json.dumps({'status': 'finding_products', 'step': 4, 'message': 'Finding product recommendations...'})}\n\n"
            products = product_finder.generate_product_recommendations(
                room_analysis, design_critique, user_preferences
            )

            if not products:
                logger.error(f"[{request_id}] No product recommendations found")
                yield f"data: {json.dumps({'error': 'No product recommendations found'})}\n\n"
                return

            logger.info(f"[{request_id}] Product recommendations generated successfully")
            logger.info(f"[{request_id}] Found {len(products)} product recommendations")

            # Final response
            response = {
                'status': 'completed',
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

            logger.info(f"[{request_id}] Streaming analysis completed successfully")
            yield f"data: {json.dumps(response)}\n\n"

        except Exception as e:
            logger.error(f"[{request_id}] Analysis failed: {str(e)}")
            logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
            yield f"data: {json.dumps({'error': f'Internal server error: {str(e)}'})}\n\n"
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                logger.info(f"[{request_id}] Cleaning up temporary file: {temp_path}")
                os.remove(temp_path)
            else:
                logger.warning(f"[{request_id}] Temporary file not found for cleanup: {temp_path}")

    return Response(generate(), mimetype='text/plain')

@app.route('/analyze', methods=['POST'])
def analyze_room():
    """
    Main endpoint for complete room analysis
    Expects: multipart/form-data with 'image' file and 'preferences' text
    """
    request_id = f"req_{int(__import__('time').time())}"
    logger.info(f"[{request_id}] Starting non-streaming room analysis request")

    try:
        # Check if image file is present
        logger.debug(f"[{request_id}] Checking for image file in request")
        if 'image' not in request.files:
            logger.error(f"[{request_id}] No image file provided in request")
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        logger.info(f"[{request_id}] Image file found: {file.filename}")
        if file.filename == '':
            logger.error(f"[{request_id}] Empty filename provided")
            return jsonify({'error': 'No image file selected'}), 400

        # Check if preferences are provided
        preferences = request.form.get('preferences')
        logger.info(f"[{request_id}] Preferences received: {len(preferences) if preferences else 0} characters")
        if not preferences:
            logger.error(f"[{request_id}] No preferences provided")
            return jsonify({'error': 'No preferences provided'}), 400

        # Validate file type
        if not allowed_file(file.filename):
            logger.error(f"[{request_id}] Invalid file type for {file.filename}")
            return jsonify({'error': f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"[{request_id}] Saving file to temporary path: {temp_path}")
        file.save(temp_path)
        logger.info(f"[{request_id}] File saved successfully ({os.path.getsize(temp_path)} bytes)")

        try:
            # Step 1: Analyze Image
            logger.info(f"[{request_id}] Starting Step 1: Image Analysis")
            room_analysis = image_analyzer.analyze_room_image(temp_path)
            if not room_analysis:
                logger.error(f"[{request_id}] Failed to analyze image")
                return jsonify({'error': 'Failed to analyze image'}), 500

            logger.info(f"[{request_id}] Image analysis completed successfully")

            # Step 2: Design Critique
            logger.info(f"[{request_id}] Starting Step 2: Design Critique")
            design_critique = design_critic.critique_design(room_analysis)
            if not design_critique:
                logger.error(f"[{request_id}] Failed to generate design critique")
                return jsonify({'error': 'Failed to generate design critique'}), 500

            logger.info(f"[{request_id}] Design critique completed successfully")

            # Step 3: Parse User Input
            logger.info(f"[{request_id}] Starting Step 3: Parse User Preferences")
            user_preferences = input_parser.parse_user_input(preferences)
            if not user_preferences or not user_preferences.get('parsed_successfully'):
                logger.error(f"[{request_id}] Failed to parse user preferences")
                return jsonify({'error': 'Failed to parse user preferences'}), 400

            logger.info(f"[{request_id}] User preferences parsed successfully")

            # Step 4: Generate Product Recommendations
            logger.info(f"[{request_id}] Starting Step 4: Generate Product Recommendations")
            products = product_finder.generate_product_recommendations(
                room_analysis, design_critique, user_preferences
            )

            if not products:
                logger.error(f"[{request_id}] No product recommendations found")
                return jsonify({'error': 'No product recommendations found'}), 404

            logger.info(f"[{request_id}] Product recommendations generated successfully")
            logger.info(f"[{request_id}] Found {len(products)} product recommendations")

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

            logger.info(f"[{request_id}] Analysis completed successfully")
            return jsonify(response)

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                logger.info(f"[{request_id}] Cleaning up temporary file: {temp_path}")
                os.remove(temp_path)
            else:
                logger.warning(f"[{request_id}] Temporary file not found for cleanup: {temp_path}")

    except Exception as e:
        logger.error(f"[{request_id}] Analysis failed: {str(e)}")
        logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/analyze/step1', methods=['POST'])
def analyze_image_only():
    """
    Step 1 only: Analyze room image
    Expects: multipart/form-data with 'image' file
    """
    request_id = f"req_{int(__import__('time').time())}"
    logger.info(f"[{request_id}] Starting Step 1 only: Image Analysis")

    try:
        if 'image' not in request.files:
            logger.error(f"[{request_id}] No image file provided in request")
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        logger.info(f"[{request_id}] Image file found: {file.filename}")
        if file.filename == '':
            logger.error(f"[{request_id}] Empty filename provided")
            return jsonify({'error': 'No image file selected'}), 400

        if not allowed_file(file.filename):
            logger.error(f"[{request_id}] Invalid file type for {file.filename}")
            return jsonify({'error': f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"[{request_id}] Saving file to temporary path: {temp_path}")
        file.save(temp_path)
        logger.info(f"[{request_id}] File saved successfully ({os.path.getsize(temp_path)} bytes)")

        try:
            room_analysis = image_analyzer.analyze_room_image(temp_path)
            if not room_analysis:
                logger.error(f"[{request_id}] Failed to analyze image")
                return jsonify({'error': 'Failed to analyze image'}), 500

            logger.info(f"[{request_id}] Image analysis completed successfully")
            return jsonify({
                'success': True,
                'room_analysis': room_analysis
            })

        finally:
            if os.path.exists(temp_path):
                logger.info(f"[{request_id}] Cleaning up temporary file: {temp_path}")
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"[{request_id}] Step 1 analysis failed: {str(e)}")
        logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/analyze/step2', methods=['POST'])
def critique_design():
    """
    Step 2: Design critique based on room analysis
    Expects: JSON with 'room_analysis' data
    """
    request_id = f"req_{int(__import__('time').time())}"
    logger.info(f"[{request_id}] Starting Step 2 only: Design Critique")

    try:
        data = request.get_json()
        logger.debug(f"[{request_id}] Received JSON data: {data is not None}")
        if not data or 'room_analysis' not in data:
            logger.error(f"[{request_id}] No room analysis data provided")
            return jsonify({'error': 'No room analysis data provided'}), 400

        logger.info(f"[{request_id}] Room analysis data received")
        design_critique = design_critic.critique_design(data['room_analysis'])
        if not design_critique:
            logger.error(f"[{request_id}] Failed to generate design critique")
            return jsonify({'error': 'Failed to generate design critique'}), 500

        logger.info(f"[{request_id}] Design critique completed successfully")
        return jsonify({
            'success': True,
            'design_critique': design_critique
        })

    except Exception as e:
        logger.error(f"[{request_id}] Step 2 analysis failed: {str(e)}")
        logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/analyze/step3', methods=['POST'])
def parse_preferences():
    """
    Step 3: Parse user preferences
    Expects: JSON with 'preferences' text
    """
    request_id = f"req_{int(__import__('time').time())}"
    logger.info(f"[{request_id}] Starting Step 3 only: Parse User Preferences")

    try:
        data = request.get_json()
        logger.debug(f"[{request_id}] Received JSON data: {data is not None}")
        if not data or 'preferences' not in data:
            logger.error(f"[{request_id}] No preferences provided")
            return jsonify({'error': 'No preferences provided'}), 400

        preferences = data['preferences']
        logger.info(f"[{request_id}] Preferences received: {len(preferences)} characters")
        user_preferences = input_parser.parse_user_input(preferences)
        if not user_preferences or not user_preferences.get('parsed_successfully'):
            logger.error(f"[{request_id}] Failed to parse user preferences")
            return jsonify({'error': 'Failed to parse user preferences'}), 400

        logger.info(f"[{request_id}] User preferences parsed successfully")
        return jsonify({
            'success': True,
            'user_preferences': user_preferences
        })

    except Exception as e:
        logger.error(f"[{request_id}] Step 3 analysis failed: {str(e)}")
        logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/analyze/step4', methods=['POST'])
def generate_recommendations():
    """
    Step 4: Generate product recommendations
    Expects: JSON with 'room_analysis', 'design_critique', 'user_preferences'
    """
    request_id = f"req_{int(__import__('time').time())}"
    logger.info(f"[{request_id}] Starting Step 4 only: Generate Product Recommendations")

    try:
        data = request.get_json()
        logger.debug(f"[{request_id}] Received JSON data: {data is not None}")
        required_fields = ['room_analysis', 'design_critique', 'user_preferences']

        for field in required_fields:
            if field not in data:
                logger.error(f"[{request_id}] Missing required field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400

        logger.info(f"[{request_id}] All required fields present")
        products = product_finder.generate_product_recommendations(
            data['room_analysis'],
            data['design_critique'],
            data['user_preferences']
        )

        if not products:
            logger.error(f"[{request_id}] No product recommendations found")
            return jsonify({'error': 'No product recommendations found'}), 404

        logger.info(f"[{request_id}] Product recommendations generated successfully")
        logger.info(f"[{request_id}] Found {len(products)} product recommendations")
        return jsonify({
            'success': True,
            'product_recommendations': products,
            'num_recommendations': len(products)
        })

    except Exception as e:
        logger.error(f"[{request_id}] Step 4 analysis failed: {str(e)}")
        logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    logger.warning("Request rejected: File too large (>16MB)")
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

@app.errorhandler(404)
def not_found(e):
    logger.warning(f"Request to unknown endpoint: {request.path}")
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    logger.warning(f"Method not allowed for endpoint: {request.method} {request.path}")
    return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    logger.info("Starting Interior Designer API Server...")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /analyze - Complete analysis (image + preferences)")
    logger.info("  POST /analyze-stream - Streaming analysis (image + preferences)")
    logger.info("  POST /analyze/step1 - Image analysis only")
    logger.info("  POST /analyze/step2 - Design critique")
    logger.info("  POST /analyze/step3 - Parse preferences")
    logger.info("  POST /analyze/step4 - Generate recommendations")
    logger.info(f"Server starting on http://localhost:8009")

    app.run(host='0.0.0.0', port=8009, debug=True)
