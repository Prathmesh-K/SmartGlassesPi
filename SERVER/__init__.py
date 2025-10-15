"""
Firebase Photo Upload Server Module

This module handles uploading photos from the Raspberry Pi to Firebase Storage
and tracking them in Firebase Realtime Database.
"""

from .photo_uploader import PhotoUploader

__all__ = ['PhotoUploader']

__version__ = '1.0.0'