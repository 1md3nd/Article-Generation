import os
import requests
import base64
from cloudinary import uploader as cloudinary_uploader
from dotenv import load_dotenv

class ImageGenerator:
    def __init__(self, engine_id="stable-diffusion-v1-6", api_host=None):
        # Load environment variables from .env file
        load_dotenv()
        # Load configuration from environment variables
        self.api_host = api_host or os.getenv('API_HOST', 'https://api.stability.ai')
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.engine_id = engine_id
        # Ensure that Stability API key is provided
        if self.api_key is None:
            raise Exception("Missing Stability API key.")
        # Cloudinary configuration
        self.cloudinary_config = {
            "cloud_name": os.getenv('CLOUDINARY_CLOUD_NAME'),
            "api_key": os.getenv("CLOUDINARY_API_KEY"),
            "api_secret": os.getenv("CLOUDINARY_API_SECRET"),
        }

    def generate_images(self, prompt, cfg_scale=7, height=1024, width=1024, samples=3, steps=30):
        try:
            # Generate images using Stability AI API
            response = requests.post(
                f"{self.api_host}/v1/generation/{self.engine_id}/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "text_prompts": [{"text": prompt}],
                    "cfg_scale": cfg_scale,
                    "height": height,
                    "width": width,
                    "samples": samples,
                    "steps": steps,
                },
            )
            response.raise_for_status()
            return response.json().get('artifacts', [])
        except Exception as e:
            print("An error occurred while generating images:", e)
            return []

    def upload_image_to_cloudinary(self, base64_string):
        try:
            # Decode the image into bytes
            image_bytes = base64.b64decode(base64_string)
            # Upload the image to Cloudinary API
            response = cloudinary_uploader.upload(image_bytes, **self.cloudinary_config)
            # Return only the public URL
            return response.get("secure_url")
        except Exception as e:
            print("An error occurred while uploading to Cloudinary:", e)
            return None
        
    def generate_and_upload_images(self, image_prompt):
        try:
            # Generate images with prompt
            image_files = self.generate_images(image_prompt)
            image_urls = []
            for image in image_files:
                # Add the public URLs
                image_url = self.upload_image_to_cloudinary(image["base64"])
                if image_url:
                    image_urls.append(image_url)
            # Return only the public image URLs
            return image_urls
        except Exception as e:
            print("An error occurred while generating and uploading images:", e)
            return []
