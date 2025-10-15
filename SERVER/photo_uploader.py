"""Photo Uploader for SmartGlassesPi - Uploads images to Supabase Storage with metadata"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import requests


class PhotoUploader:
    """Handles uploading photos to Supabase Storage with metadata"""
    
    CONTENT_TYPES = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp"
    }
    
    def __init__(self, supabase_url=None, supabase_key=None, bucket_name="Photos"):
        """Initialize PhotoUploader with Supabase credentials"""
        self.supabase_url = supabase_url or os.getenv(
            "SUPABASE_URL", 
            "https://nrjtstpywrjxldpaxkjx.supabase.co"
        )
        self.supabase_key = supabase_key or os.getenv(
            "SUPABASE_KEY",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5yanRzdHB5d3JqeGxkcGF4a2p4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA1MjAwMzEsImV4cCI6MjA3NjA5NjAzMX0.YCv6okLn4kYF-fMiyQo2rkq0lKjtDJpcmpNx0Ywcf7Q"
        )
        self.bucket_name = bucket_name
    
    def upload(self, file_path, device_id="pi_001", context=None, ocr_text=None, **metadata):
        """Upload photo to Supabase with metadata"""
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}
        
        # Read file
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Generate filename and get content type
        filename = f"{uuid.uuid4()}{path.suffix}"
        content_type = self.CONTENT_TYPES.get(path.suffix.lower(), "image/jpeg")
        
        # Build metadata
        meta = {"uploaded_at": datetime.utcnow().isoformat()}
        if device_id:
            meta["device_id"] = device_id
        if context:
            meta["context"] = context
        if ocr_text:
            meta["ocr_text"] = ocr_text
        meta.update(metadata)
        
        # Upload
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": content_type,
            "x-upsert": "false",
            "x-metadata": json.dumps(meta)
        }
        
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"
        
        try:
            response = requests.post(url, headers=headers, data=content, timeout=30)
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "filename": filename,
                    "url": f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}",
                    "metadata": meta
                }
            return {"success": False, "error": f"Upload failed: {response.status_code}", "details": response.text}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
