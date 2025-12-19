import os
from datetime import datetime
from app.utils.db import get_db


def upload_image_to_storage(file, filename=None):
    """
    Upload an image file to Supabase Storage.

    Args:
        file: File object or file path
        filename: Optional custom filename. If not provided, generates one.

    Returns:
        dict: {
            'success': bool,
            'url': str or None,
            'path': str or None,
            'error': str or None
        }
    """
    try:
        db = get_db()

        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            ext = os.path.splitext(file.filename)[1] if hasattr(file, 'filename') else '.jpg'
            filename = f"{timestamp}{ext}"

        # Supabase storage bucket name
        bucket_name = 'issues'

        # Upload file to Supabase Storage
        if hasattr(file, 'read'):
            # File object
            file_data = file.read()
            file.seek(0)  # Reset file pointer for potential re-use
        else:
            # File path
            with open(file, 'rb') as f:
                file_data = f.read()

        # Upload to storage
        result = db.storage.from_(bucket_name).upload(
            path=filename,
            file=file_data,
            file_options={'content-type': 'image/jpeg'}
        )

        # Get public URL
        public_url = db.storage.from_(bucket_name).get_public_url(filename)

        return {
            'success': True,
            'url': public_url,
            'path': filename,
            'error': None
        }

    except Exception as e:
        return {
            'success': False,
            'url': None,
            'path': None,
            'error': str(e)
        }


def delete_image_from_storage(image_path):
    """
    Delete an image from Supabase Storage.

    Args:
        image_path: Path to the image in storage (just the filename)

    Returns:
        dict: {
            'success': bool,
            'error': str or None
        }
    """
    try:
        db = get_db()
        bucket_name = 'issues'

        db.storage.from_(bucket_name).remove([image_path])

        return {
            'success': True,
            'error': None
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
