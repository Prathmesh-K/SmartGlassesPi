"""
Photo Uploader Module

Handles uploading images to Firebase Storage blob storage.
"""

import firebase_admin
from firebase_admin import credentials, storage
import os
from datetime import datetime


class PhotoUploader:
    """Handles uploading photos to Firebase Storage"""
    
    def __init__(self, credentials_path, storage_bucket):
        """
        Initialize Firebase Storage uploader
        
        Args:
            credentials_path: Path to Firebase service account JSON file
            storage_bucket: Firebase storage bucket name (e.g., 'project-id.appspot.com')
        """
        self.credentials_path = credentials_path
        self.storage_bucket = storage_bucket
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase app and storage bucket"""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Firebase credentials not found: {self.credentials_path}")
        
        # Initialize Firebase only if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.credentials_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': self.storage_bucket
            })
        
        self.bucket = storage.bucket()
    
    def upload_photo(self, local_image_path, remote_path=None, make_public=True):
        """
        Upload a photo to Firebase Storage
        
        Args:
            local_image_path: Path to the local image file on the Pi
            remote_path: Optional custom path/filename in storage. 
                        If None, generates timestamp-based path
            make_public: Whether to make the uploaded image publicly accessible
            
        Returns:
            str: Public URL of the uploaded image if make_public=True, 
                 otherwise the blob name
                 
        Raises:
            FileNotFoundError: If local image doesn't exist
            Exception: If upload fails
        """
        # Validate local file exists
        if not os.path.exists(local_image_path):
            raise FileNotFoundError(f"Image file not found: {local_image_path}")
        
        # Generate remote path if not provided
        if remote_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = os.path.basename(local_image_path)
            name, ext = os.path.splitext(filename)
            remote_path = f"photos/{timestamp}{ext}"
        
        try:
            # Create blob reference and upload
            blob = self.bucket.blob(remote_path)
            blob.upload_from_filename(local_image_path)
            
            # Make publicly accessible if requested
            if make_public:
                blob.make_public()
                return blob.public_url
            else:
                return blob.name
                
        except Exception as e:
            raise Exception(f"Failed to upload photo: {str(e)}")
    
    def delete_photo(self, remote_path):
        """
        Delete a photo from Firebase Storage
        
        Args:
            remote_path: Path to the file in Firebase Storage
            
        Returns:
            bool: True if deletion successful
        """
        try:
            blob = self.bucket.blob(remote_path)
            blob.delete()
            return True
        except Exception as e:
            raise Exception(f"Failed to delete photo: {str(e)}")
    
    def get_photo_url(self, remote_path):
        """
        Get the public URL for a photo
        
        Args:
            remote_path: Path to the file in Firebase Storage
            
        Returns:
            str: Public URL of the photo
        """
        blob = self.bucket.blob(remote_path)
        blob.make_public()
        return blob.public_url