from flask import render_template, request, jsonify
from app.blueprints.map import map_bp
from app.utils.auth import login_required
from app.utils.db import get_db


@map_bp.route('/')
@login_required
def index():
    """Map view displaying reported issues with markers and filters"""
    # Fetch issue types for the filter dropdown
    try:
        db = get_db()
        result = db.table('issue_types').select('id, name').eq('active', True).order('name').execute()
        issue_types = result.data
    except Exception as e:
        print(f"Error loading issue types: {e}")
        issue_types = []

    return render_template('map/map.html', issue_types=issue_types)


@map_bp.route('/api/markers')
@login_required
def get_markers():
    """API endpoint to fetch issue markers for the map"""
    try:
        db = get_db()

        # Start building query - only get issues with valid coordinates
        query = db.table('issues').select('id, latitude, longitude, timestamp, image_url, issue_types(name)')

        # Filter out issues with extraction errors
        query = query.eq('extraction_error', False)

        # Apply filters from query parameters
        issue_type_id = request.args.get('issue_type')
        if issue_type_id:
            query = query.eq('issue_type_id', int(issue_type_id))

        date_from = request.args.get('date_from')
        if date_from:
            query = query.gte('timestamp', date_from)

        date_to = request.args.get('date_to')
        if date_to:
            query = query.lte('timestamp', date_to)

        # Execute query
        result = query.execute()
        issues = result.data

        # Format markers for frontend
        markers = []
        for issue in issues:
            # Skip issues without coordinates
            if issue['latitude'] is None or issue['longitude'] is None:
                continue

            markers.append({
                'id': issue['id'],
                'lat': float(issue['latitude']),
                'lng': float(issue['longitude']),
                'type': issue['issue_types']['name'] if issue.get('issue_types') else 'Unknown',
                'timestamp': issue['timestamp'],
                'image_url': issue['image_url']
            })

        return jsonify(markers)

    except Exception as e:
        print(f"Error fetching markers: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
