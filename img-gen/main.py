from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import uvicorn
import os
import math
from typing import List, Literal
from pydantic import BaseModel
import requests
import json
import logging
import time
import traceback
from datetime import datetime
import base64
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image Generation API")

logger.info("Initializing Google GenAI client...")
client = genai.Client()
logger.info("FastAPI application initialized")
logger.info("Google GenAI client initialized successfully")

# Style-specific prompts
logger.info("Loading style-specific prompts...")
STYLE_PROMPTS = {
    "modern": "Apply a modern interior design style with clean lines, minimalist aesthetics, neutral colors, and contemporary furniture. Focus on simplicity, functionality, and sleek surfaces.",
    "scandinavian": "Apply a Scandinavian interior design style with light woods, white and light colors, cozy textures, natural materials, and hygge-inspired elements. Emphasize simplicity, functionality, and natural light.",
    "industrial": "Apply an industrial interior design style with exposed brick, metal fixtures, dark colors, raw materials, concrete elements, and vintage industrial furniture. Focus on urban, warehouse-like aesthetics.",
    "bohemian": "Apply a bohemian interior design style with rich colors, eclectic patterns, layered textiles, vintage furniture, plants, and artistic elements. Emphasize creativity, warmth, and global influences.",
    "midcentury modern": "Apply a mid-century modern interior design style with clean geometric lines, warm wood tones, bold colors, iconic furniture pieces from the 1950s-60s, and retro elements.",
    "traditional": "Apply a traditional interior design style with classic furniture, rich fabrics, ornate details, warm colors, elegant patterns, and timeless decorative elements."
}
logger.info(f"Loaded {len(STYLE_PROMPTS)} style prompts: {list(STYLE_PROMPTS.keys())}")

def download_image(url: str) -> Image.Image:
    """Download an image from a URL (HTTP or data URL) and return a PIL Image."""
    logger.info(f"Attempting to download image from URL: {url[:50]}...")
    start_time = time.time()

    try:
        # Handle data URLs
        if url.startswith('data:'):
            import base64
            import re
            
            # Parse data URL: data:image/jpeg;base64,<base64_data>
            match = re.match(r'data:([^;]+);base64,(.+)', url)
            if not match:
                raise Exception("Invalid data URL format")
            
            mime_type, base64_data = match.groups()
            image_data = base64.b64decode(base64_data)
            
            download_time = time.time() - start_time
            logger.info(f"Successfully decoded data URL in {download_time:.2f}s")
            
            image = Image.open(BytesIO(image_data))
            logger.info(f"Image loaded: {image.size[0]}x{image.size[1]} pixels, mode: {image.mode}")
            return image
            
        # Handle HTTP URLs
        else:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            download_time = time.time() - start_time
            logger.info(f"Successfully downloaded image from {url} in {download_time:.2f}s")

            image = Image.open(BytesIO(response.content))
            logger.info(f"Image loaded: {image.size[0]}x{image.size[1]} pixels, mode: {image.mode}")

            return image
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while downloading image from {url}")
        raise Exception(f"Timeout while downloading image from {url}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error downloading image from {url}: {str(e)}")
        raise Exception(f"Failed to download image from {url}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error downloading image from {url}: {str(e)}")
        raise Exception(f"Failed to download image from {url}: {str(e)}")

def optimize_image_for_api(image: Image.Image, max_dimension: int = 1024) -> Image.Image:
    """Optimize image size for API to prevent timeouts."""
    width, height = image.size
    logger.debug(f"Optimizing image - original size: {width}x{height}")
    
    # Only resize if image is larger than max_dimension
    if max(width, height) > max_dimension:
        # Calculate new dimensions while maintaining aspect ratio
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        
        logger.info(f"Resizing image from {width}x{height} to {new_width}x{new_height}")
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.info(f"Image resizing completed successfully")
    else:
        logger.debug(f"Image size {width}x{height} is within limits, no resizing needed")
    
    return image

def create_montage(images: List[Image.Image], max_cell_size: int = 512) -> Image.Image:
    """Create a compact, space-efficient square montage from a list of images."""
    logger.info(f"Creating montage from {len(images)} images with max cell size {max_cell_size}")
    start_time = time.time()

    if not images:
        logger.error("No images provided for montage creation")
        raise ValueError("No images provided for montage")

    # Calculate grid dimensions (as square as possible)
    num_images = len(images)
    grid_cols = math.ceil(math.sqrt(num_images))
    grid_rows = math.ceil(num_images / grid_cols)  # Only as many rows as needed

    logger.info(f"Calculated montage grid: {grid_cols}x{grid_rows} for {num_images} images")

    # Find the maximum dimensions among all images
    max_width = max(img.width for img in images)
    max_height = max(img.height for img in images)
    
    # Cap the cell size to prevent pathologically large montages
    if max_width > max_cell_size or max_height > max_cell_size:
        # Scale down to fit within max_cell_size while maintaining aspect ratio
        if max_width > max_height:
            scale_factor = max_cell_size / max_width
        else:
            scale_factor = max_cell_size / max_height
        
        max_width = int(max_width * scale_factor)
        max_height = int(max_height * scale_factor)
        logger.info(f"Capped montage cell size to {max_width}x{max_height} pixels")

    logger.info(f"Max dimensions found: {max_width}x{max_height}")

    # Create a new image for the montage with exact dimensions (no padding)
    montage_width = grid_cols * max_width
    montage_height = grid_rows * max_height  # Use actual rows needed
    montage = Image.new('RGB', (montage_width, montage_height), (255, 255, 255))

    logger.info(f"Created montage canvas: {montage_width}x{montage_height}")

    # Place images in the grid with no margins or padding
    for i, img in enumerate(images):
        row = i // grid_cols
        col = i % grid_cols

        # Resize image to exactly fit the grid cell
        img_resized = img.resize((max_width, max_height), Image.Resampling.LANCZOS)

        # Place image directly in grid position (no centering offset)
        x_offset = col * max_width
        y_offset = row * max_height

        montage.paste(img_resized, (x_offset, y_offset))
        logger.debug(f"Placed image {i+1} at position ({col}, {row}) - offset ({x_offset}, {y_offset})")

    montage_time = time.time() - start_time
    logger.info(f"Montage creation completed in {montage_time:.2f}s")
    return montage


class ProcessImageRequest(BaseModel):
    product_names: List[str]
    image_urls: List[str]
    custom_prompt: str = "Incorporate these products naturally into this room scene"
    style: Literal["modern", "scandinavian", "industrial", "bohemian", "midcentury modern", "traditional"] = "modern"

@app.post("/process-image-stream")
async def process_image_stream(
    file: UploadFile = File(...),
    product_names: str = Form(...),  # JSON string of product names
    image_urls: str = Form(...),  # JSON string of image URLs
    custom_prompt: str = Form(default="Incorporate these products naturally into this room scene"),
    style: str = Form(default="modern")  # Interior design style
):
    """
    Process an uploaded room image with product images downloaded from URLs and return streaming JSON responses.
    """
    request_id = f"req_{int(time.time())}"
    
    # Read the uploaded room image BEFORE starting the streaming response
    logger.info(f"[{request_id}] Reading uploaded room image before streaming")
    room_image_data = await file.read()
    logger.info(f"[{request_id}] Successfully read {len(room_image_data)} bytes of room image data")
    
    async def generate():
        try:
            yield f"data: {json.dumps({'status': 'started', 'request_id': request_id, 'message': 'Starting image processing...'})}\n\n"
            await asyncio.sleep(0.1)  # Allow client to receive first message
            
            logger.info(f"[{request_id}] Starting image processing request")
            logger.info(f"[{request_id}] File: {file.filename}, Content-Type: {file.content_type}")
            logger.info(f"[{request_id}] Style: {style}, Custom prompt: {custom_prompt}")

            start_time = time.time()

            if not file.content_type or not file.content_type.startswith('image/'):
                logger.error(f"[{request_id}] Invalid file type: {file.content_type}")
                yield f"data: {json.dumps({'error': 'File must be an image'})}\n\n"
                return

            # Parse product names and image URLs
            yield f"data: {json.dumps({'status': 'parsing', 'message': 'Parsing product names and URLs...'})}\n\n"
            await asyncio.sleep(0.1)
            
            logger.info(f"[{request_id}] Parsing product names and image URLs")
            try:
                names = json.loads(product_names)
                urls = json.loads(image_urls)
                logger.info(f"[{request_id}] Parsed {len(names)} product names and {len(urls)} URLs")

                if not isinstance(names, list) or not isinstance(urls, list):
                    raise ValueError("Must be lists")
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"[{request_id}] JSON parsing error: {str(e)}")
                yield f"data: {json.dumps({'error': 'product_names and image_urls must be valid JSON arrays'})}\n\n"
                return

            # Validate style parameter
            valid_styles = ["modern", "scandinavian", "industrial", "bohemian", "midcentury modern", "traditional"]
            if style not in valid_styles:
                logger.error(f"[{request_id}] Invalid style: {style}")
                yield f"data: {json.dumps({'error': f'Invalid style. Must be one of: {', '.join(valid_styles)}'})}\n\n"
                return

            # Load the pre-read room image
            yield f"data: {json.dumps({'status': 'loading_room', 'message': 'Loading room image...'})}\n\n"
            await asyncio.sleep(0.1)
            
            logger.info(f"[{request_id}] Loading pre-read room image data")
            room_image = Image.open(BytesIO(room_image_data))
            logger.info(f"[{request_id}] Room image loaded: {room_image.size[0]}x{room_image.size[1]} pixels, mode: {room_image.mode}")
            
            # Optimize room image for API
            room_image = optimize_image_for_api(room_image)
            logger.info(f"[{request_id}] Room image optimized to: {room_image.size[0]}x{room_image.size[1]} pixels")

            # Download images from URLs
            yield f"data: {json.dumps({'status': 'downloading', 'message': f'Downloading {len(urls)} product images...'})}\n\n"
            await asyncio.sleep(0.1)
            
            logger.info(f"[{request_id}] Starting download of {len(urls)} product images")
            product_images = []
            failed_downloads = []

            for i, url in enumerate(urls):
                try:
                    yield f"data: {json.dumps({'status': 'downloading', 'message': f'Downloading image {i+1}/{len(urls)}...'})}\n\n"
                    await asyncio.sleep(0.1)
                    
                    logger.info(f"[{request_id}] Downloading image {i+1}/{len(urls)} from URL: {url[:50]}...")
                    img = download_image(url)
                    # Optimize each product image for API
                    img = optimize_image_for_api(img)
                    product_images.append(img)
                    logger.info(f"[{request_id}] Successfully downloaded and optimized image {i+1}/{len(urls)}")
                except Exception as e:
                    error_msg = f"URL {i+1} ({url}): {str(e)}"
                    logger.error(f"[{request_id}] {error_msg}")
                    failed_downloads.append(error_msg)

            if failed_downloads:
                logger.error(f"[{request_id}] Failed downloads: {len(failed_downloads)}")
                yield f"data: {json.dumps({'error': f'Failed to download images: {'; '.join(failed_downloads)}'})}\n\n"
                return

            if not product_images:
                logger.error(f"[{request_id}] No valid product images downloaded")
                yield f"data: {json.dumps({'error': 'No valid product images downloaded'})}\n\n"
                return

            logger.info(f"[{request_id}] Successfully downloaded {len(product_images)} product images")

            # Create montage from downloaded images
            yield f"data: {json.dumps({'status': 'creating_montage', 'message': 'Creating product montage...'})}\n\n"
            await asyncio.sleep(0.1)
            
            logger.info(f"[{request_id}] Creating montage from product images")
            montage = create_montage(product_images)

            # Get style-specific prompt
            style_prompt = STYLE_PROMPTS[style]
            logger.info(f"[{request_id}] Using style prompt for '{style}' style")
            logger.debug(f"[{request_id}] Style prompt: {style_prompt[:100]}...")

            # Generate content using room image and montage
            yield f"data: {json.dumps({'status': 'generating', 'message': 'Generating image with AI...'})}\n\n"
            await asyncio.sleep(0.1)
            
            logger.info(f"[{request_id}] Starting AI image generation with Gemini")
            logger.info(f"[{request_id}] Model: gemini-2.5-flash-image-preview")
            generation_start = time.time()

            # Convert PIL images to bytes for the API
            logger.info(f"[{request_id}] Converting room image to bytes for API")
            room_image_bytes = BytesIO()
            room_image.save(room_image_bytes, format='PNG')
            room_image_bytes = room_image_bytes.getvalue()
            logger.info(f"[{request_id}] Room image converted to {len(room_image_bytes)} bytes")

            logger.info(f"[{request_id}] Converting montage to bytes for API")
            montage_bytes = BytesIO()
            montage.save(montage_bytes, format='PNG')
            montage_bytes = montage_bytes.getvalue()
            logger.info(f"[{request_id}] Montage converted to {len(montage_bytes)} bytes")

            logger.info("Calling generate_content")
            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[
                    "Room image to modify: [This is the base room scene]",
                    types.Part.from_bytes(data=room_image_bytes, mime_type="image/png"),
                    "Product montage to incorporate: [These products should be naturally placed in the room]",
                    types.Part.from_bytes(data=montage_bytes, mime_type="image/png"),
                    f"Style instructions: {style_prompt}",
                    f"Additional instructions: {custom_prompt}"
                ],
            )

            generation_time = time.time() - generation_start
            logger.info(f"[{request_id}] AI generation completed in {generation_time:.2f}s")

            # Find the generated image in the response
            yield f"data: {json.dumps({'status': 'processing_result', 'message': 'Processing AI response...'})}\n\n"
            await asyncio.sleep(0.1)
            
            logger.info(f"[{request_id}] Processing AI response")
            logger.info(f"[{request_id}] Response has {len(response.candidates)} candidate(s)")
            for i, part in enumerate(response.candidates[0].content.parts):
                logger.debug(f"[{request_id}] Processing part {i+1}: has_inline_data={part.inline_data is not None}")
                if part.inline_data is not None:
                    logger.info(f"[{request_id}] Found generated image in response part {i+1}")
                    logger.info(f"[{request_id}] Generated image size: {len(part.inline_data.data)} bytes")

                    # Encode image as base64
                    generated_image_base64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                    logger.info(f"[{request_id}] Generated image encoded as base64 ({len(generated_image_base64)} chars)")
                    
                    total_time = time.time() - start_time
                    logger.info(f"[{request_id}] Request completed successfully in {total_time:.2f}s")

                    # Return final result without embedding large base64 in JSON
                    # First send completion status
                    completion_result = {
                        'status': 'completed',
                        'success': True,
                        'request_id': request_id,
                        'processing_time': total_time,
                        'generated_image': {
                            'content_type': 'image/png',
                            'filename': 'room_with_products.png',
                            'size': len(generated_image_base64)
                        }
                    }
                    
                    yield f"data: {json.dumps(completion_result)}\n\n"
                    
                    # Then send the base64 data in a separate, simpler JSON structure
                    image_data_result = {
                        'status': 'image_data',
                        'data': generated_image_base64
                    }
                    
                    yield f"data: {json.dumps(image_data_result)}\n\n"
                    return

            logger.error(f"[{request_id}] No image found in AI response")
            yield f"data: {json.dumps({'error': 'No image generated in response'})}\n\n"

        except Exception as e:
            logger.error(f"[{request_id}] Request failed: {str(e)}")
            logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
            yield f"data: {json.dumps({'error': f'Error processing image: {str(e)}'})}\n\n"

    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/process-image-json")
async def process_image_json(
    file: UploadFile = File(...),
    product_names: str = Form(...),  # JSON string of product names
    image_urls: str = Form(...),  # JSON string of image URLs
    custom_prompt: str = Form(default="Incorporate these products naturally into this room scene"),
    style: str = Form(default="modern")  # Interior design style
):
    """
    Process an uploaded room image with product images downloaded from URLs and return JSON with base64 image.
    Similar to streaming endpoint but returns structured JSON response instead of streaming.
    """
    request_id = f"req_{int(time.time())}"
    logger.info(f"[{request_id}] Starting JSON image processing request")
    logger.info(f"[{request_id}] File: {file.filename}, Content-Type: {file.content_type}")
    logger.info(f"[{request_id}] Style: {style}, Custom prompt: {custom_prompt}")

    start_time = time.time()

    if not file.content_type or not file.content_type.startswith('image/'):
        logger.error(f"[{request_id}] Invalid file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Parse product names and image URLs
        logger.info(f"[{request_id}] Parsing product names and image URLs")
        try:
            names = json.loads(product_names)
            urls = json.loads(image_urls)
            logger.info(f"[{request_id}] Parsed {len(names)} product names and {len(urls)} URLs")

            if not isinstance(names, list) or not isinstance(urls, list):
                raise ValueError("Must be lists")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"[{request_id}] JSON parsing error: {str(e)}")
            raise HTTPException(status_code=400, detail="product_names and image_urls must be valid JSON arrays")

        # Validate style parameter
        valid_styles = ["modern", "scandinavian", "industrial", "bohemian", "midcentury modern", "traditional"]
        if style not in valid_styles:
            logger.error(f"[{request_id}] Invalid style: {style}")
            raise HTTPException(status_code=400, detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}")

        # Read the uploaded room image
        logger.info(f"[{request_id}] Reading uploaded room image")
        room_image_data = await file.read()
        room_image = Image.open(BytesIO(room_image_data))
        logger.info(f"[{request_id}] Room image loaded: {room_image.size[0]}x{room_image.size[1]} pixels, mode: {room_image.mode}")
        
        # Optimize room image for API
        room_image = optimize_image_for_api(room_image)
        logger.info(f"[{request_id}] Room image optimized to: {room_image.size[0]}x{room_image.size[1]} pixels")

        # Download images from URLs
        logger.info(f"[{request_id}] Starting download of {len(urls)} product images")
        product_images = []
        failed_downloads = []

        for i, url in enumerate(urls):
            try:
                logger.info(f"[{request_id}] Downloading image {i+1}/{len(urls)} from URL: {url[:50]}...")
                img = download_image(url)
                # Optimize each product image for API
                img = optimize_image_for_api(img)
                product_images.append(img)
                logger.info(f"[{request_id}] Successfully downloaded and optimized image {i+1}/{len(urls)}")
            except Exception as e:
                error_msg = f"URL {i+1} ({url}): {str(e)}"
                logger.error(f"[{request_id}] {error_msg}")
                failed_downloads.append(error_msg)

        if failed_downloads:
            logger.error(f"[{request_id}] Failed downloads: {len(failed_downloads)}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download images: {'; '.join(failed_downloads)}"
            )

        if not product_images:
            logger.error(f"[{request_id}] No valid product images downloaded")
            raise HTTPException(status_code=400, detail="No valid product images downloaded")

        logger.info(f"[{request_id}] Successfully downloaded {len(product_images)} product images")

        # Create montage from downloaded images
        logger.info(f"[{request_id}] Creating montage from product images")
        montage = create_montage(product_images)

        # Get style-specific prompt
        style_prompt = STYLE_PROMPTS[style]
        logger.info(f"[{request_id}] Using style prompt for '{style}' style")

        # Generate content using room image and montage
        logger.info(f"[{request_id}] Starting AI image generation with Gemini")
        generation_start = time.time()

        # Convert PIL images to bytes for the API
        logger.info(f"[{request_id}] Converting room image to bytes for API")
        room_image_bytes = BytesIO()
        room_image.save(room_image_bytes, format='PNG')
        room_image_bytes = room_image_bytes.getvalue()

        logger.info(f"[{request_id}] Converting montage to bytes for API")
        montage_bytes = BytesIO()
        montage.save(montage_bytes, format='PNG')
        montage_bytes = montage_bytes.getvalue()

        logger.info("Calling generate_content")
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[
                "Room image to modify: [This is the base room scene]",
                types.Part.from_bytes(data=room_image_bytes, mime_type="image/png"),
                "Product montage to incorporate: [These products should be naturally placed in the room]",
                types.Part.from_bytes(data=montage_bytes, mime_type="image/png"),
                f"Style instructions: {style_prompt}",
                f"Additional instructions: {custom_prompt}"
            ],
        )

        generation_time = time.time() - generation_start
        logger.info(f"[{request_id}] AI generation completed in {generation_time:.2f}s")

        # Find the generated image in the response
        logger.info(f"[{request_id}] Processing AI response")
        for i, part in enumerate(response.candidates[0].content.parts):
            if part.inline_data is not None:
                logger.info(f"[{request_id}] Found generated image in response part {i+1}")
                
                # Encode image as base64
                generated_image_base64 = base64.b64encode(part.inline_data.data).decode('utf-8')
                logger.info(f"[{request_id}] Generated image encoded as base64 ({len(generated_image_base64)} chars)")
                
                total_time = time.time() - start_time
                logger.info(f"[{request_id}] Request completed successfully in {total_time:.2f}s")

                # Return JSON response with base64 image
                return {
                    'status': 'completed',
                    'success': True,
                    'request_id': request_id,
                    'processing_time': total_time,
                    'generated_image': {
                        'data': generated_image_base64,
                        'content_type': 'image/png',
                        'filename': 'room_with_products.png',
                        'size': len(generated_image_base64)
                    }
                }

        logger.error(f"[{request_id}] No image found in AI response")
        raise HTTPException(status_code=500, detail="No image generated in response")

    except HTTPException:
        logger.error(f"[{request_id}] HTTP exception occurred")
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[{request_id}] Request failed after {total_time:.2f}s: {str(e)}")
        logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/process-image")
async def process_image(
    file: UploadFile = File(...),
    product_names: str = Form(...),  # JSON string of product names
    image_urls: str = Form(...),  # JSON string of image URLs
    custom_prompt: str = Form(default="Incorporate these products naturally into this room scene"),
    style: str = Form(default="modern")  # Interior design style
):
    """
    Process an uploaded room image with product images downloaded from URLs and return the result.
    """
    request_id = f"req_{int(time.time())}"
    logger.info(f"[{request_id}] Starting image processing request")
    logger.info(f"[{request_id}] File: {file.filename}, Content-Type: {file.content_type}")
    logger.info(f"[{request_id}] Style: {style}, Custom prompt: {custom_prompt}")

    start_time = time.time()

    if not file.content_type or not file.content_type.startswith('image/'):
        logger.error(f"[{request_id}] Invalid file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Parse product names and image URLs
        logger.info(f"[{request_id}] Parsing product names and image URLs")
        logger.debug(f"[{request_id}] Raw product_names: {product_names[:100]}...")
        logger.debug(f"[{request_id}] Raw image_urls: {image_urls[:100]}...")
        try:
            names = json.loads(product_names)
            urls = json.loads(image_urls)
            logger.info(f"[{request_id}] Parsed {len(names)} product names and {len(urls)} URLs")

            if not isinstance(names, list) or not isinstance(urls, list):
                raise ValueError("Must be lists")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"[{request_id}] JSON parsing error: {str(e)}")
            raise HTTPException(status_code=400, detail="product_names and image_urls must be valid JSON arrays")

        # Validate style parameter
        valid_styles = ["modern", "scandinavian", "industrial", "bohemian", "midcentury modern", "traditional"]
        if style not in valid_styles:
            logger.error(f"[{request_id}] Invalid style: {style}")
            raise HTTPException(status_code=400, detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}")

        # Read the uploaded room image
        logger.info(f"[{request_id}] Reading uploaded room image")
        room_image_data = await file.read()
        room_image = Image.open(BytesIO(room_image_data))
        logger.info(f"[{request_id}] Room image loaded: {room_image.size[0]}x{room_image.size[1]} pixels, mode: {room_image.mode}")
        
        # Optimize room image for API
        room_image = optimize_image_for_api(room_image)
        logger.info(f"[{request_id}] Room image optimized to: {room_image.size[0]}x{room_image.size[1]} pixels")

        # Download images from URLs
        logger.info(f"[{request_id}] Starting download of {len(urls)} product images")
        product_images = []
        failed_downloads = []

        for i, url in enumerate(urls):
            try:
                logger.info(f"[{request_id}] Downloading image {i+1}/{len(urls)} from URL: {url[:50]}...")
                img = download_image(url)
                # Optimize each product image for API
                img = optimize_image_for_api(img)
                product_images.append(img)
                logger.info(f"[{request_id}] Successfully downloaded and optimized image {i+1}/{len(urls)}")
            except Exception as e:
                error_msg = f"URL {i+1} ({url}): {str(e)}"
                logger.error(f"[{request_id}] {error_msg}")
                failed_downloads.append(error_msg)

        if failed_downloads:
            logger.error(f"[{request_id}] Failed downloads: {len(failed_downloads)}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download images: {'; '.join(failed_downloads)}"
            )

        if not product_images:
            logger.error(f"[{request_id}] No valid product images downloaded")
            raise HTTPException(status_code=400, detail="No valid product images downloaded")

        logger.info(f"[{request_id}] Successfully downloaded {len(product_images)} product images")

        # Create montage from downloaded images
        logger.info(f"[{request_id}] Creating montage from product images")
        montage = create_montage(product_images)

        # Get style-specific prompt
        style_prompt = STYLE_PROMPTS[style]
        logger.info(f"[{request_id}] Using style prompt for '{style}' style")
        logger.debug(f"[{request_id}] Style prompt: {style_prompt[:100]}...")

        # Generate content using room image and montage
        logger.info(f"[{request_id}] Starting AI image generation with Gemini")
        logger.info(f"[{request_id}] Model: gemini-2.5-flash-image-preview")
        generation_start = time.time()

        # Convert PIL images to bytes for the API
        logger.info(f"[{request_id}] Converting room image to bytes for API")
        room_image_bytes = BytesIO()
        room_image.save(room_image_bytes, format='PNG')
        room_image_bytes = room_image_bytes.getvalue()
        logger.info(f"[{request_id}] Room image converted to {len(room_image_bytes)} bytes")
        with open("/tmp/room_image.png", 'wb') as f:
            f.write(room_image_bytes)
            logger.debug(f"[{request_id}] Saved room image debug copy to /tmp/room_image.png")

        logger.info(f"[{request_id}] Converting montage to bytes for API")
        montage_bytes = BytesIO()
        montage.save(montage_bytes, format='PNG')
        montage_bytes = montage_bytes.getvalue()
        logger.info(f"[{request_id}] Montage converted to {len(montage_bytes)} bytes")
        with open("/tmp/montage_bytes.png", 'wb') as f:
            f.write(montage_bytes)
            logger.debug(f"[{request_id}] Saved montage debug copy to /tmp/montage_bytes.png")

        logger.info("Calling generate_content")
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[
                "Room image to modify: [This is the base room scene]",
                types.Part.from_bytes(data=room_image_bytes, mime_type="image/png"),
                "Product montage to incorporate: [These products should be naturally placed in the room]",
                types.Part.from_bytes(data=montage_bytes, mime_type="image/png"),
                f"Style instructions: {style_prompt}",
                f"Additional instructions: {custom_prompt}"
            ],
        )

        generation_time = time.time() - generation_start
        logger.info(f"[{request_id}] AI generation completed in {generation_time:.2f}s")

        # Find the generated image in the response
        logger.info(f"[{request_id}] Processing AI response")
        logger.info(f"[{request_id}] Response has {len(response.candidates)} candidate(s)")
        for i, part in enumerate(response.candidates[0].content.parts):
            logger.debug(f"[{request_id}] Processing part {i+1}: has_inline_data={part.inline_data is not None}")
            if part.inline_data is not None:
                logger.info(f"[{request_id}] Found generated image in response part {i+1}")
                logger.info(f"[{request_id}] Generated image size: {len(part.inline_data.data)} bytes")

                # Return the generated image
                result_image_data = BytesIO(part.inline_data.data)

                total_time = time.time() - start_time
                logger.info(f"[{request_id}] Request completed successfully in {total_time:.2f}s")

                return StreamingResponse(
                    result_image_data,
                    media_type="image/png",
                    headers={
                        "Content-Disposition": "attachment; filename=room_with_products.png"
                    }
                )

        logger.error(f"[{request_id}] No image found in AI response")
        raise HTTPException(status_code=500, detail="No image generated in response")

    except HTTPException:
        logger.error(f"[{request_id}] HTTP exception occurred")
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"[{request_id}] Request failed after {total_time:.2f}s: {str(e)}")
        logger.error(f"[{request_id}] Exception traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint."""
    logger.info("Root endpoint accessed")
    return {"message": "Image Generation API is running"}

def main():
    logger.info("Starting FastAPI server on host 0.0.0.0, port 8005")
    uvicorn.run(app, host="0.0.0.0", port=8005)

if __name__ == "__main__":
    logger.info("Application started directly")
    main()
