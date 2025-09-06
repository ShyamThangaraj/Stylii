from main import create_montage
from PIL import Image
from pathlib import Path
import requests
import json

def test_montage():
    imgs = [Image.open(f) for f in Path("tests/imgs").iterdir()]
    montage = create_montage(imgs)
    montage.save("montage.png")

def test_process_image():
    # post request to /process-image, as specified in main.py
    url = "http://localhost:8005/process-image/"

    # Use local resized images instead of URLs
    product_names = ["Modern Chair", "Coffee Table"]

    # Convert local images to base64 for URLs (simulating what would be real URLs)
    import base64
    import os

    local_image_paths = ["tests/chair.jpg", "tests/table.jpg"]
    image_urls = []

    # Create data URLs from local files
    for path in local_image_paths:
        with open(path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
            mime_type = "image/jpeg"
            data_url = f"data:{mime_type};base64,{img_data}"
            image_urls.append(data_url)

    # Create test image file (or use existing one)
    test_image_path = "tests/imgs/room.jpg"  # assuming this exists

    # Prepare form data
    data = {
        "product_names": json.dumps(product_names),
        "image_urls": json.dumps(image_urls),
        "custom_prompt": "Incorporate these products naturally into this room scene. IMPORTANT: You **MUST** maintain the original room photo's aspect ratio and perspective. DO NOT expand the photo to include parts of the room not in the original photo.",
        "style": "modern"
    }

    # Open and send the image file
    with open(test_image_path, "rb") as f:
        files = {"file": ("room.jpg", f, "image/jpeg")}

        print("Calling requests.post...")
        response = requests.post(url, data=data, files=files)

        if response.status_code == 200:
            # Save the result image
            with open("generated_room.png", "wb") as output_file:
                output_file.write(response.content)
            print("Successfully generated image saved as 'generated_room.png'")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    # test_montage()
    test_process_image()
