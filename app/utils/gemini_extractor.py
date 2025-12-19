import os
import re
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel, Part


def initialize_gemini():
    """Initialize Vertex AI with credentials from environment."""
    project_id = os.getenv('GCP_PROJECT_ID')
    location = os.getenv('GCP_LOCATION')

    if not project_id or not location:
        raise ValueError('GCP_PROJECT_ID and GCP_LOCATION must be set in environment')

    vertexai.init(project=project_id, location=location)


def extract_watermark_data(image_path):
    """
    Extract GPS coordinates and timestamp from image watermarks using Gemini Vision.

    Args:
        image_path: Path to the image file

    Returns:
        dict: {
            'latitude': float or None,
            'longitude': float or None,
            'timestamp': datetime or None,
            'raw_text': str or None
        }
    """
    result = {
        'latitude': None,
        'longitude': None,
        'timestamp': None,
        'raw_text': None
    }

    try:
        print("  → Initializing Gemini...")
        # Initialize Gemini
        initialize_gemini()
        print("  → Gemini initialized successfully")

        # Load the image
        print(f"  → Loading image from {image_path}...")
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        print(f"  → Image loaded, size: {len(image_bytes)} bytes")

        # Create the model
        print("  → Creating GenerativeModel...")
        model = GenerativeModel('gemini-2.0-flash-001')
        print("  → Model created")

        # Create the prompt
        prompt = """
        You are analyzing a photo taken by a citizen reporting an issue to city hall. The photo has a watermark overlay at the bottom with GPS location information and timestamp.

        IMPORTANT: Look carefully at the bottom of the image for text overlays showing location data.

        Extract the following information from ANY visible text watermarks:

        1. GPS COORDINATES - Look for patterns like:
           - "Lat 44.513561° Long 26.021965°"
           - "44.513561, 26.021965"
           - "N 44°30'48.8" E 26°01'19.1""
           - Any numbers that look like latitude and longitude (latitude is typically -90 to 90, longitude -180 to 180)

        2. TIMESTAMP - Look for dates and times like:
           - "19/11/24 09:50 AM"
           - "2024-11-19 09:50:00"
           - "19.11.2024 09:50"
           - Any date/time pattern

        3. LOCATION NAME/ADDRESS - Extract any street names, city names, or addresses you see

        Return ONLY the extracted values in this EXACT format:
        LATITUDE: <decimal number>
        LONGITUDE: <decimal number>
        TIMESTAMP: <convert to YYYY-MM-DD HH:MM:SS format, for example 2024-11-19 09:50:00>
        LOCATION: <address or location name if visible>

        For fields you cannot find, write "NOT FOUND"

        CRITICAL: Focus on the watermark text at the bottom of the image. Read it character by character. The coordinates are there!
        """

        # Generate response
        print("  → Calling Gemini API...")
        response = model.generate_content([
            Part.from_data(image_bytes, mime_type='image/jpeg'),
            prompt
        ])
        print("  → Gemini API call completed")

        if response and hasattr(response, 'text') and response.text:
            print(f"  → Gemini returned text: {response.text[:200]}...")
            result['raw_text'] = response.text
            result = _parse_gemini_response(response.text)
        else:
            print("  → WARNING: Gemini returned empty response")
            print(f"  → Response object: {response}")

        return result

    except Exception as e:
        # Log the error and return empty result
        print(f"  → ERROR in Gemini extraction: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return result


def _parse_gemini_response(text):
    """
    Parse Gemini's response to extract GPS coordinates and timestamp.

    Args:
        text: Response text from Gemini

    Returns:
        dict: Parsed data
    """
    result = {
        'latitude': None,
        'longitude': None,
        'timestamp': None,
        'raw_text': text
    }

    # Extract latitude - try multiple patterns
    lat_match = re.search(r'LATITUDE:\s*([+-]?\d+\.?\d*)', text, re.IGNORECASE)
    if lat_match:
        try:
            result['latitude'] = float(lat_match.group(1))
        except ValueError:
            pass

    # Extract longitude - try multiple patterns
    lon_match = re.search(r'LONGITUDE:\s*([+-]?\d+\.?\d*)', text, re.IGNORECASE)
    if lon_match:
        try:
            result['longitude'] = float(lon_match.group(1))
        except ValueError:
            pass

    # Extract timestamp
    timestamp_match = re.search(r'TIMESTAMP:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if timestamp_match:
        timestamp_str = timestamp_match.group(1).strip()
        if timestamp_str.upper() != 'NOT FOUND':
            result['timestamp'] = _parse_timestamp(timestamp_str)

    # If structured format didn't work, try to find coordinates in the full text
    if result['latitude'] is None or result['longitude'] is None:
        # Try pattern: "Lat XX.XXXXX° Long YY.YYYYY°"
        lat_long_pattern = re.search(r'Lat\s+([+-]?\d+\.?\d*)[°\s]+Long\s+([+-]?\d+\.?\d*)', text, re.IGNORECASE)
        if lat_long_pattern:
            try:
                result['latitude'] = float(lat_long_pattern.group(1))
                result['longitude'] = float(lat_long_pattern.group(2))
            except ValueError:
                pass

        # Try pattern: "XX.XXXXX, YY.YYYYY"
        if result['latitude'] is None or result['longitude'] is None:
            coord_match = re.search(r'([+-]?\d+\.\d+)\s*,?\s*([+-]?\d+\.\d+)', text)
            if coord_match:
                try:
                    lat = float(coord_match.group(1))
                    lon = float(coord_match.group(2))
                    # Validate ranges
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        result['latitude'] = lat
                        result['longitude'] = lon
                except ValueError:
                    pass

    return result


def _parse_timestamp(timestamp_str):
    """
    Parse timestamp from Gemini's standardized format.

    Args:
        timestamp_str: String representation of timestamp in YYYY-MM-DD HH:MM:SS format

    Returns:
        datetime or None
    """
    try:
        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None
