import os
import tempfile
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from app.blueprints.upload import upload_bp
from app.utils.auth import login_required
from app.utils.db import get_db
from app.utils.gemini_extractor import extract_watermark_data
from app.utils.storage import upload_image_to_storage


@upload_bp.route('/')
@login_required
def index():
    """Upload page with multi-file input and issue type selection"""
    # Fetch issue types from database
    try:
        db = get_db()
        result = db.table('issue_types').select('id, name').eq('active', True).order('name').execute()
        issue_types = result.data
    except Exception as e:
        flash(f'Error loading issue types: {str(e)}', 'error')
        issue_types = []

    return render_template('upload.html', issue_types=issue_types)


@upload_bp.route('/process', methods=['POST'])
@login_required
def process_upload():
    """Handle file upload and metadata extraction"""
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files[]')
    issue_types = request.form.getlist('issue_types[]')

    if len(files) != len(issue_types):
        return jsonify({'error': 'Mismatch between files and issue types'}), 400

    db = get_db()
    success_count = 0
    failed_count = 0
    failed_details = []

    for idx, file in enumerate(files):
        issue_type_id = issue_types[idx]
        temp_path = None
        filename = file.filename

        try:
            print(f"\n{'='*60}")
            print(f"Processing file {idx + 1}/{len(files)}: {filename}")
            print(f"Issue type ID: {issue_type_id}")

            # Save file to temp location for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                file.save(temp_file.name)
                temp_path = temp_file.name
            print(f"✓ File saved to temp: {temp_path}")

            # Extract GPS and timestamp using Gemini (primary method)
            print("Starting Gemini extraction...")
            extracted_data = extract_watermark_data(temp_path)

            latitude = extracted_data.get('latitude')
            longitude = extracted_data.get('longitude')
            timestamp = extracted_data.get('timestamp')
            raw_text = extracted_data.get('raw_text')

            print(f"✓ Gemini extraction complete:")
            print(f"  - Latitude: {latitude}")
            print(f"  - Longitude: {longitude}")
            print(f"  - Timestamp: {timestamp}")
            print(f"  - Raw text: {raw_text[:100] if raw_text else None}...")

            # Upload image to Supabase Storage
            file.seek(0)  # Reset file pointer
            print("Uploading to Supabase Storage...")
            storage_result = upload_image_to_storage(file)

            if not storage_result['success']:
                raise Exception(f"Storage upload failed: {storage_result['error']}")

            print(f"✓ Image uploaded to storage:")
            print(f"  - URL: {storage_result['url']}")
            print(f"  - Path: {storage_result['path']}")

            # Check if extraction was successful
            has_error = latitude is None or longitude is None

            # Save to database
            issue_data = {
                'issue_type_id': int(issue_type_id),
                'latitude': latitude,
                'longitude': longitude,
                'timestamp': timestamp.isoformat() if timestamp else None,
                'image_url': storage_result['url'],
                'image_path': storage_result['path'],
                'extraction_error': has_error,
                'error_message': 'Failed to extract GPS coordinates' if has_error else None,
                'raw_extraction_text': raw_text
            }

            print(f"Saving to database...")
            print(f"  - Issue data: {issue_data}")
            result = db.table('issues').insert(issue_data).execute()
            print(f"✓ Saved to database. Result: {result}")

            success_count += 1
            print(f"✓ File {filename} processed successfully!")

        except Exception as e:
            failed_count += 1
            error_msg = str(e)
            print(f"✗ Error processing {filename}: {error_msg}")
            import traceback
            traceback.print_exc()
            failed_details.append({
                'filename': filename,
                'error': error_msg
            })

        finally:
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"✓ Cleaned up temp file")

    results = {
        'success': success_count,
        'failed': failed_count,
        'total': len(files),
        'failed_details': failed_details
    }

    return jsonify(results)


@upload_bp.route('/errors')
@login_required
def errors():
    """Page showing images that failed processing"""
    try:
        db = get_db()
        result = db.table('issues').select('*, issue_types(name)').eq('extraction_error', True).order('created_at', desc=True).execute()
        failed_uploads = result.data
    except Exception as e:
        flash(f'Error loading failed uploads: {str(e)}', 'error')
        failed_uploads = []

    return render_template('upload_errors.html', failed_uploads=failed_uploads)
