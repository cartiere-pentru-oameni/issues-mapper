from PIL import Image
import piexif
from datetime import datetime


def extract_exif_data(image_path):
    """
    Extract GPS coordinates and timestamp from image EXIF data.

    Returns:
        dict: {
            'latitude': float or None,
            'longitude': float or None,
            'timestamp': datetime or None,
            'has_exif': bool
        }
    """
    result = {
        'latitude': None,
        'longitude': None,
        'timestamp': None,
        'has_exif': False
    }

    try:
        image = Image.open(image_path)

        # Check if image has EXIF data
        if 'exif' not in image.info:
            return result

        exif_dict = piexif.load(image.info['exif'])
        result['has_exif'] = True

        # Extract GPS data
        if piexif.GPSIFD.GPSLatitude in exif_dict['GPS'] and piexif.GPSIFD.GPSLongitude in exif_dict['GPS']:
            gps_latitude = exif_dict['GPS'][piexif.GPSIFD.GPSLatitude]
            gps_latitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
            gps_longitude = exif_dict['GPS'][piexif.GPSIFD.GPSLongitude]
            gps_longitude_ref = exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')

            # Convert GPS coordinates to decimal format
            lat = _convert_to_degrees(gps_latitude)
            if gps_latitude_ref == 'S':
                lat = -lat

            lon = _convert_to_degrees(gps_longitude)
            if gps_longitude_ref == 'W':
                lon = -lon

            result['latitude'] = lat
            result['longitude'] = lon

        # Extract timestamp
        if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
            datetime_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
            try:
                result['timestamp'] = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
            except ValueError:
                pass

        return result

    except Exception as e:
        # If any error occurs, return empty result
        return result


def _convert_to_degrees(value):
    """
    Convert GPS coordinates from DMS (degrees, minutes, seconds) to decimal degrees.

    Args:
        value: tuple of tuples ((degrees_num, degrees_den), (minutes_num, minutes_den), (seconds_num, seconds_den))

    Returns:
        float: decimal degrees
    """
    d = value[0][0] / value[0][1]
    m = value[1][0] / value[1][1]
    s = value[2][0] / value[2][1]

    return d + (m / 60.0) + (s / 3600.0)
