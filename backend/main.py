from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import time
from datetime import datetime
import httpx
import json
import logging
from io import BytesIO
from typing import Dict, Any

app = FastAPI(title="Nano Banana Hackathon API", version="1.0.0")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
DESIGNER_SERVICE_URL = "http://localhost:8009"
IMG_GEN_SERVICE_URL = "http://localhost:8005"

# Add CORS middleware to allow frontend to communicate with backend
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

@app.post("/designer")
async def designer_endpoint(
    image: UploadFile = File(...),
    preferences: str = Form(...)
):
    """
    Master endpoint that:
    1. Sends image and preferences to designer service
    2. Extracts product thumbnails from designer response
    3. Sends original image and thumbnails to img-gen service
    4. Returns both the generated image and designer JSON
    """
    request_id = f"req_{int(time.time())}"
    logger.info(f"[{request_id}] Starting designer endpoint request")
    
    try:
        # Step 1: Call designer service
        logger.info(f"[{request_id}] Calling designer service")
        
        # Read image data for designer service
        image_data = await image.read()
        
        # Prepare form data for designer service
        files = {"image": (image.filename, BytesIO(image_data), image.content_type)}
        data = {"preferences": preferences}
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            designer_response = await client.post(
                f"{DESIGNER_SERVICE_URL}/analyze",
                files=files,
                data=data
            )
            
        if designer_response.status_code != 200:
            logger.error(f"[{request_id}] Designer service error: {designer_response.status_code}")
            raise HTTPException(
                status_code=designer_response.status_code,
                detail=f"Designer service error: {designer_response.text}"
            )
            
        designer_data = designer_response.json()
        logger.info(f"[{request_id}] Designer service responded successfully")
        
        # Step 2: Extract product thumbnails
        product_recommendations = designer_data.get("product_recommendations", [])
        if not product_recommendations:
            logger.warning(f"[{request_id}] No product recommendations found")
            raise HTTPException(status_code=404, detail="No product recommendations found")
            
        # Extract thumbnail URLs and product names
        thumbnail_urls = []
        product_names = []
        for product in product_recommendations:
            if "thumbnail" in product and "title" in product:
                thumbnail_urls.append(product["thumbnail"])
                product_names.append(product["title"])
        
        if not thumbnail_urls:
            logger.warning(f"[{request_id}] No valid thumbnail URLs found")
            raise HTTPException(status_code=404, detail="No valid product thumbnails found")
            
        logger.info(f"[{request_id}] Extracted {len(thumbnail_urls)} product thumbnails")
        
        # Step 3: Call img-gen service
        logger.info(f"[{request_id}] Calling img-gen service")
        
        # Reset image data stream for img-gen service
        image_bytes = BytesIO(image_data)
        
        # Prepare form data for img-gen service
        img_gen_files = {"file": (image.filename, image_bytes, image.content_type)}
        img_gen_data = {
            "product_names": json.dumps(product_names),
            "image_urls": json.dumps(thumbnail_urls),
            "custom_prompt": "Incorporate these products naturally into this room scene",
            "style": "modern"  # Could be extracted from preferences in the future
        }
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            img_gen_response = await client.post(
                f"{IMG_GEN_SERVICE_URL}/process-image",
                files=img_gen_files,
                data=img_gen_data
            )
            
        if img_gen_response.status_code != 200:
            logger.error(f"[{request_id}] Img-gen service error: {img_gen_response.status_code}")
            raise HTTPException(
                status_code=img_gen_response.status_code,
                detail=f"Image generation service error: {img_gen_response.text}"
            )
            
        logger.info(f"[{request_id}] Image generation completed successfully")
        
        # Step 4: Return combined response
        # The img-gen service returns the generated image as a streaming response
        # We need to read it and return it along with the designer data
        
        generated_image_data = img_gen_response.content
        
        # For now, we'll return the designer JSON in headers and the image as content
        # In a real implementation, you might want to return a multipart response
        # or store the image and return a URL
        
        response_headers = {
            "X-Designer-Data": json.dumps(designer_data),
            "Content-Type": "image/png",
            "Content-Disposition": "attachment; filename=generated_room.png"
        }
        
        logger.info(f"[{request_id}] Request completed successfully")
        
        return StreamingResponse(
            BytesIO(generated_image_data),
            media_type="image/png",
            headers=response_headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/designer-json")
async def designer_json_endpoint(
    image: UploadFile = File(...),
    preferences: str = Form(...)
):
    """
    Alternative endpoint that returns a JSON response with both designer data and base64-encoded generated image.
    This avoids potential header size limitations and provides a more structured response.
    """
    import base64
    
    request_id = f"req_{int(time.time())}"
    logger.info(f"[{request_id}] Starting designer-json endpoint request")
    
    try:
        # Step 1: Call designer service
        logger.info(f"[{request_id}] Calling designer service")
        
        # Read image data for designer service
        image_data = await image.read()
        
        # Prepare form data for designer service
        files = {"image": (image.filename, BytesIO(image_data), image.content_type)}
        data = {"preferences": preferences}
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            designer_response = await client.post(
                f"{DESIGNER_SERVICE_URL}/analyze",
                files=files,
                data=data
            )
            
        if designer_response.status_code != 200:
            logger.error(f"[{request_id}] Designer service error: {designer_response.status_code}")
            raise HTTPException(
                status_code=designer_response.status_code,
                detail=f"Designer service error: {designer_response.text}"
            )
            
        designer_data = designer_response.json()
        logger.info(f"[{request_id}] Designer service responded successfully")
        
        # Step 2: Extract product thumbnails
        product_recommendations = designer_data.get("product_recommendations", [])
        if not product_recommendations:
            logger.warning(f"[{request_id}] No product recommendations found")
            raise HTTPException(status_code=404, detail="No product recommendations found")
            
        # Extract thumbnail URLs and product names
        thumbnail_urls = []
        product_names = []
        for product in product_recommendations:
            if "thumbnail" in product and "title" in product:
                thumbnail_urls.append(product["thumbnail"])
                product_names.append(product["title"])
        
        if not thumbnail_urls:
            logger.warning(f"[{request_id}] No valid thumbnail URLs found")
            raise HTTPException(status_code=404, detail="No valid product thumbnails found")
            
        logger.info(f"[{request_id}] Extracted {len(thumbnail_urls)} product thumbnails")
        
        # Step 3: Call img-gen service
        logger.info(f"[{request_id}] Calling img-gen service")
        
        # Reset image data stream for img-gen service
        image_bytes = BytesIO(image_data)
        
        # Prepare form data for img-gen service
        img_gen_files = {"file": (image.filename, image_bytes, image.content_type)}
        img_gen_data = {
            "product_names": json.dumps(product_names),
            "image_urls": json.dumps(thumbnail_urls),
            "custom_prompt": "Incorporate these products naturally into this room scene",
            "style": "modern"  # Could be extracted from preferences in the future
        }
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            img_gen_response = await client.post(
                f"{IMG_GEN_SERVICE_URL}/process-image",
                files=img_gen_files,
                data=img_gen_data
            )
            
        if img_gen_response.status_code != 200:
            logger.error(f"[{request_id}] Img-gen service error: {img_gen_response.status_code}")
            raise HTTPException(
                status_code=img_gen_response.status_code,
                detail=f"Image generation service error: {img_gen_response.text}"
            )
            
        logger.info(f"[{request_id}] Image generation completed successfully")
        
        # Step 4: Prepare combined JSON response
        generated_image_data = img_gen_response.content
        generated_image_base64 = base64.b64encode(generated_image_data).decode('utf-8')
        
        response_data = {
            "success": True,
            "designer_data": designer_data,
            "generated_image": {
                "data": generated_image_base64,
                "content_type": "image/png",
                "filename": "generated_room.png"
            },
            "request_id": request_id
        }
        
        logger.info(f"[{request_id}] Request completed successfully")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI backend!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/status")
async def status_check():
    """Detailed status endpoint for frontend to check backend health"""
    return {
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
            "designer": "/designer",
            "designer-json": "/designer-json"
        }
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint for frontend to verify backend connectivity"""
    return {
        "message": "Backend is working correctly!",
        "timestamp": datetime.now().isoformat(),
        "cors_enabled": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
