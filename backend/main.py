from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import time
from datetime import datetime
import httpx
import json
import logging
import traceback
from io import BytesIO
from typing import Dict, Any
import asyncio
import base64

app = FastAPI(title="Nano Banana Hackathon API", version="1.0.0")

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Service URLs
DESIGNER_SERVICE_URL = "http://localhost:8009"
IMG_GEN_SERVICE_URL = "http://localhost:8005"

# Add CORS middleware to allow frontend to communicate with backend
logger.info("Setting up CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default port
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://localhost:3001",  # Alternative port
        "http://127.0.0.1:3001",  # Alternative port with 127.0.0.1
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured successfully")

@app.post("/design")
async def design_endpoint(
    image: UploadFile = File(...),
    preferences: str = Form(...)
):
    """
    Master streaming endpoint that:
    1. Streams designer analysis progress
    2. Streams image generation progress
    3. Returns final JSON with base64-encoded generated image
    """
    request_id = f"req_{int(time.time())}"
    logger.info(f"[{request_id}] Starting streaming design endpoint request")

    # Read image data BEFORE starting the streaming response
    logger.info(f"[{request_id}] Reading image data before streaming")
    image_data = await image.read()
    logger.info(f"[{request_id}] Successfully read {len(image_data)} bytes of image data")

    async def stream_response():
        try:
            # Initial status
            yield f"data: {json.dumps({'status': 'started', 'request_id': request_id, 'message': 'Starting room design process...'})}\n\n"
            await asyncio.sleep(0.1)

            # Step 1: Call designer service with streaming
            logger.info(f"[{request_id}] Starting designer service streaming")
            logger.info(f"[{request_id}] Designer service URL: {DESIGNER_SERVICE_URL}/analyze-stream")
            yield f"data: {json.dumps({'status': 'designer_started', 'message': 'Analyzing room and finding products...'})}\n\n"
            await asyncio.sleep(0.1)

            # Prepare form data for designer service with fresh BytesIO
            logger.info(f"[{request_id}] Creating BytesIO for designer service")
            image_stream = BytesIO(image_data)
            files = {"image": (image.filename, image_stream, image.content_type)}
            data = {"preferences": preferences}
            logger.info(f"[{request_id}] Created files dict for designer service")

            designer_data = None

            # Stream from designer service
            logger.info(f"[{request_id}] Initiating HTTP streaming request to designer service")
            async with httpx.AsyncClient(timeout=120.0) as client:
                logger.info(f"[{request_id}] Created httpx.AsyncClient with 120s timeout")
                async with client.stream(
                    "POST",
                    f"{DESIGNER_SERVICE_URL}/analyze-stream",
                    files=files,
                    data=data
                ) as designer_response:
                    logger.info(f"[{request_id}] Designer service response status: {designer_response.status_code}")

                    if designer_response.status_code != 200:
                        logger.error(f"[{request_id}] Designer service error: {designer_response.status_code}")
                        yield f"data: {json.dumps({'error': f'Designer service error: {designer_response.status_code}'})}\n\n"
                        return

                    logger.info(f"[{request_id}] Starting to process designer service streaming response")
                    async for chunk in designer_response.aiter_text():
                        if chunk.strip():
                            logger.info(f"[{request_id}] Received chunk from designer service: {chunk[:100]}...")
                            for line in chunk.strip().split('\n'):
                                if line.startswith('data: '):
                                    try:
                                        chunk_data = json.loads(line[6:])  # Remove 'data: ' prefix
                                        logger.info(f"[{request_id}] Parsed designer chunk data: {chunk_data.get('status', 'unknown')}")

                                        # Forward designer progress updates
                                        if 'status' in chunk_data and chunk_data['status'] != 'completed':
                                            yield f"data: {json.dumps({'status': 'designer_progress', 'designer_status': chunk_data.get('status'), 'message': chunk_data.get('message', '')})}\n\n"
                                            await asyncio.sleep(0.1)
                                        elif chunk_data.get('status') == 'completed':
                                            designer_data = chunk_data
                                            logger.info(f"[{request_id}] Designer service completed successfully")
                                            yield f"data: {json.dumps({'status': 'designer_completed', 'message': 'Room analysis complete!'})}\n\n"
                                            await asyncio.sleep(0.1)
                                        elif 'error' in chunk_data:
                                            logger.error(f"[{request_id}] Designer service returned error: {chunk_data['error']}")
                                            yield f"data: {json.dumps({'error': f'Designer error: {chunk_data["error"]}'})}\n\n"
                                            return
                                    except json.JSONDecodeError as e:
                                        logger.warning(f"[{request_id}] Failed to parse designer chunk JSON: {e}")
                                        continue

            if not designer_data:
                logger.error(f"[{request_id}] No data received from designer service")
                yield f"data: {json.dumps({'error': 'No data received from designer service'})}\n\n"
                return

            # Step 2: Extract product thumbnails
            logger.info(f"[{request_id}] Extracting product thumbnails from designer data")
            product_recommendations = designer_data.get("product_recommendations", [])
            logger.info(f"[{request_id}] Found {len(product_recommendations)} product recommendations")
            if not product_recommendations:
                logger.warning(f"[{request_id}] No product recommendations found")
                yield f"data: {json.dumps({'error': 'No product recommendations found'})}\n\n"
                return

            # Extract thumbnail URLs and product names
            thumbnail_urls = []
            product_names = []
            for i, product in enumerate(product_recommendations):
                if "thumbnail" in product and "title" in product:
                    thumbnail_urls.append(product["thumbnail"])
                    product_names.append(product["title"])
                    logger.info(f"[{request_id}] Product {i+1}: {product['title']} -> {product['thumbnail']}")
                else:
                    logger.warning(f"[{request_id}] Product {i+1} missing thumbnail or title: {product}")

            if not thumbnail_urls:
                logger.warning(f"[{request_id}] No valid thumbnail URLs found")
                yield f"data: {json.dumps({'error': 'No valid product thumbnails found'})}\n\n"
                return

            logger.info(f"[{request_id}] Extracted {len(thumbnail_urls)} product thumbnails")

            # Step 3: Call img-gen service with streaming
            logger.info(f"[{request_id}] Starting image generation streaming")
            logger.info(f"[{request_id}] Image generation service URL: {IMG_GEN_SERVICE_URL}/process-image-stream")
            yield f"data: {json.dumps({'status': 'generation_started', 'message': 'Generating new room design...'})}\n\n"
            await asyncio.sleep(0.1)

            # Reset image data stream for img-gen service
            logger.info(f"[{request_id}] Preparing image data for img-gen service")
            image_bytes = BytesIO(image_data)

            # Prepare form data for img-gen service
            img_gen_files = {"file": (image.filename, image_bytes, image.content_type)}
            img_gen_data = {
                "product_names": json.dumps(product_names),
                "image_urls": json.dumps(thumbnail_urls),
                "custom_prompt": "Incorporate these products naturally into this room scene",
                "style": "modern"
            }
            logger.info(f"[{request_id}] Prepared form data for img-gen service with {len(product_names)} products")

            generated_image_data = None
            generated_image_base64 = None

            # Stream from img-gen service
            logger.info(f"[{request_id}] Initiating HTTP streaming request to img-gen service")
            async with httpx.AsyncClient(timeout=180.0) as client:
                logger.info(f"[{request_id}] Created httpx.AsyncClient with 180s timeout for image generation")
                async with client.stream(
                    "POST",
                    f"{IMG_GEN_SERVICE_URL}/process-image-stream",
                    files=img_gen_files,
                    data=img_gen_data
                ) as img_gen_response:
                    logger.info(f"[{request_id}] Image generation service response status: {img_gen_response.status_code}")

                    if img_gen_response.status_code != 200:
                        logger.error(f"[{request_id}] Img-gen service error: {img_gen_response.status_code}")
                        yield f"data: {json.dumps({'error': f'Image generation service error: {img_gen_response.status_code}'})}\n\n"
                        return

                    logger.info(f"[{request_id}] Starting to process img-gen service streaming response")
                    buffer = ""  # Buffer to accumulate partial JSON data
                    async for chunk in img_gen_response.aiter_text():
                        if chunk.strip():
                            logger.info(f"[{request_id}] Received chunk from img-gen service: {chunk[:100]}...")
                            buffer += chunk
                            
                            # Process complete SSE messages in the buffer
                            while '\n\n' in buffer:
                                line_end = buffer.find('\n\n')
                                complete_message = buffer[:line_end]
                                buffer = buffer[line_end + 2:]
                                
                                # Process the complete SSE message
                                if complete_message.startswith('data: '):
                                    try:
                                        chunk_data = json.loads(complete_message[6:])  # Remove 'data: ' prefix
                                        logger.info(f"[{request_id}] Parsed img-gen chunk data: {chunk_data.get('status', 'unknown')}")

                                        # Forward img-gen progress updates
                                        if 'status' in chunk_data and chunk_data['status'] not in ['completed', 'image_data']:
                                            yield f"data: {json.dumps({'status': 'generation_progress', 'generation_status': chunk_data.get('status'), 'message': chunk_data.get('message', '')})}\n\n"
                                            await asyncio.sleep(0.1)
                                        elif chunk_data.get('status') == 'completed':
                                            generated_image_data = chunk_data
                                            logger.info(f"[{request_id}] Image generation completed successfully")
                                            yield f"data: {json.dumps({'status': 'generation_completed', 'message': 'Image generation complete!'})}\n\n"
                                            await asyncio.sleep(0.1)
                                        elif chunk_data.get('status') == 'image_data':
                                            # Receive the base64 image data separately
                                            generated_image_base64 = chunk_data.get('data')
                                            logger.info(f"[{request_id}] Received base64 image data ({len(generated_image_base64) if generated_image_base64 else 0} chars)")
                                        elif 'error' in chunk_data:
                                            logger.error(f"[{request_id}] Image generation service returned error: {chunk_data['error']}")
                                            yield f"data: {json.dumps({'error': f'Generation error: {chunk_data["error"]}'})}\n\n"
                                            return
                                    except json.JSONDecodeError as e:
                                        logger.warning(f"[{request_id}] Failed to parse img-gen chunk JSON: {e}")
                                        logger.warning(f"[{request_id}] Problematic message: {complete_message[:200]}...")
                                        continue

            if not generated_image_data or not generated_image_base64:
                logger.error(f"[{request_id}] Incomplete image data received from img-gen service")
                yield f"data: {json.dumps({'error': 'Incomplete image data received'})}\n\n"
                return

            # Step 4: Return final combined response
            logger.info(f"[{request_id}] Preparing final response")
            logger.info(f"[{request_id}] Final response includes: designer_data, generated_image, summary")

            final_response = {
                'status': 'completed',
                'success': True,
                'designer_data': designer_data,
                'generated_image': {
                    'data': generated_image_base64,
                    'content_type': generated_image_data.get('generated_image', {}).get('content_type', 'image/png'),
                    'filename': generated_image_data.get('generated_image', {}).get('filename', 'room_with_products.png')
                },
                'request_id': request_id,
                'summary': {
                    'room_type': designer_data.get('room_analysis', {}).get('room_type', 'Unknown'),
                    'current_style': designer_data.get('room_analysis', {}).get('current_style', 'Unknown'),
                    'budget': designer_data.get('user_preferences', {}).get('budget_amount', 0),
                    'num_recommendations': len(product_recommendations)
                }
            }

            yield f"data: {json.dumps(final_response)}\n\n"
            logger.info(f"[{request_id}] Streaming request completed successfully")

        except HTTPException:
            logger.error(f"[{request_id}] HTTP exception occurred")
            raise
        except Exception as e:
            logger.error(f"[{request_id}] Unexpected error: {str(e)}")
            logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
            yield f"data: {json.dumps({'error': f'Internal server error: {str(e)}'})}\n\n"

    return StreamingResponse(stream_response(), media_type="text/plain")


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Hello from FastAPI backend!"}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}

@app.get("/status")
async def status_check():
    """Detailed status endpoint for frontend to check backend health"""
    logger.info("Status check endpoint accessed")
    status_data = {
        "status": "running",
        "service": "FastAPI Backend",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "active",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "docs": "/docs",
            "test": "/test",
            "design": "/design"
        }
    }
    logger.info(f"Returning status data: {status_data}")
    return status_data

@app.post("/design-sync")
async def design_endpoint_sync(
    image: UploadFile = File(...),
    preferences: str = Form(...)
):
    """
    Non-streaming design endpoint that:
    1. Calls designer service (non-streaming)
    2. Calls image generation service (non-streaming)
    3. Returns final JSON with base64-encoded generated image
    """
    request_id = f"req_{int(time.time())}"
    logger.info(f"[{request_id}] Starting non-streaming design endpoint request")

    try:
        # Read image data
        logger.info(f"[{request_id}] Reading image data")
        image_data = await image.read()
        logger.info(f"[{request_id}] Successfully read {len(image_data)} bytes of image data")

        # Step 1: Call designer service (non-streaming)
        logger.info(f"[{request_id}] Calling designer service")
        image_stream = BytesIO(image_data)
        files = {"image": (image.filename, image_stream, image.content_type)}
        data = {"preferences": preferences}

        async with httpx.AsyncClient(timeout=120.0) as client:
            designer_response = await client.post(
                f"{DESIGNER_SERVICE_URL}/analyze",
                files=files,
                data=data
            )
            
            if designer_response.status_code != 200:
                logger.error(f"[{request_id}] Designer service error: {designer_response.status_code}")
                raise HTTPException(status_code=500, detail=f"Designer service error: {designer_response.status_code}")

            designer_data = designer_response.json()
            logger.info(f"[{request_id}] Designer service completed successfully")

        # Step 2: Extract product thumbnails
        logger.info(f"[{request_id}] Extracting product thumbnails from designer data")
        product_recommendations = designer_data.get("product_recommendations", [])
        logger.info(f"[{request_id}] Found {len(product_recommendations)} product recommendations")
        
        if not product_recommendations:
            logger.warning(f"[{request_id}] No product recommendations found")
            raise HTTPException(status_code=404, detail="No product recommendations found")

        # Extract thumbnail URLs and product names
        thumbnail_urls = []
        product_names = []
        for i, product in enumerate(product_recommendations):
            if "thumbnail" in product and "title" in product:
                thumbnail_urls.append(product["thumbnail"])
                product_names.append(product["title"])
                logger.info(f"[{request_id}] Product {i+1}: {product['title']} -> {product['thumbnail']}")

        if not thumbnail_urls:
            logger.warning(f"[{request_id}] No valid thumbnail URLs found")
            raise HTTPException(status_code=404, detail="No valid product thumbnails found")

        logger.info(f"[{request_id}] Extracted {len(thumbnail_urls)} product thumbnails")

        # Step 3: Call img-gen service (non-streaming)
        logger.info(f"[{request_id}] Calling image generation service")
        image_bytes = BytesIO(image_data)
        img_gen_files = {"file": (image.filename, image_bytes, image.content_type)}
        img_gen_data = {
            "product_names": json.dumps(product_names),
            "image_urls": json.dumps(thumbnail_urls),
            "custom_prompt": "Incorporate these products naturally into this room scene",
            "style": "modern"
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            img_gen_response = await client.post(
                f"{IMG_GEN_SERVICE_URL}/process-image-json",
                files=img_gen_files,
                data=img_gen_data
            )
            
            if img_gen_response.status_code != 200:
                logger.error(f"[{request_id}] Img-gen service error: {img_gen_response.status_code}")
                raise HTTPException(status_code=500, detail=f"Image generation service error: {img_gen_response.status_code}")

            # The /process-image-json endpoint returns JSON with base64 image data
            generated_image_response = img_gen_response.json()
            generated_image_base64 = generated_image_response.get('generated_image', {}).get('data')
            if not generated_image_base64:
                logger.error(f"[{request_id}] No image data in img-gen response")
                raise HTTPException(status_code=500, detail="No image data received from generation service")
            
            logger.info(f"[{request_id}] Image generation completed successfully")

        # Step 4: Return final combined response
        logger.info(f"[{request_id}] Preparing final response")
        final_response = {
            'status': 'completed',
            'success': True,
            'designer_data': designer_data,
            'generated_image': {
                'data': generated_image_base64,
                'content_type': 'image/png',
                'filename': 'room_with_products.png'
            },
            'request_id': request_id,
            'summary': {
                'room_type': designer_data.get('room_analysis', {}).get('room_type', 'Unknown'),
                'current_style': designer_data.get('room_analysis', {}).get('current_style', 'Unknown'),
                'budget': designer_data.get('user_preferences', {}).get('budget_amount', 0),
                'num_recommendations': len(product_recommendations)
            }
        }

        logger.info(f"[{request_id}] Non-streaming request completed successfully")
        return final_response

    except HTTPException:
        logger.error(f"[{request_id}] HTTP exception occurred")
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}")
        logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/test")
async def test_endpoint():
    """Test endpoint for frontend to verify backend connectivity"""
    logger.info("Test endpoint accessed")
    test_data = {
        "message": "Backend is working correctly!",
        "timestamp": datetime.now().isoformat(),
        "cors_enabled": True
    }
    logger.info(f"Returning test data: {test_data}")
    return test_data

if __name__ == "__main__":
    logger.info("Starting FastAPI backend server")
    logger.info("Server configuration: host=0.0.0.0, port=8000")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
