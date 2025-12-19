from flask import render_template, jsonify
from app.blueprints.statistics import statistics_bp
from app.utils.auth import login_required
from app.utils.db import get_db
from datetime import datetime, timedelta


@statistics_bp.route('/')
@login_required
def index():
    """Statistics dashboard with charts and graphs"""
    return render_template('statistics/statistics.html')


@statistics_bp.route('/api/summary')
@login_required
def get_summary():
    """Get summary statistics"""
    try:
        db = get_db()

        # Total issues
        total_result = db.table('issues').select('id', count='exact').execute()
        total_issues = total_result.count

        # Issues with successful extraction
        successful_result = db.table('issues').select('id', count='exact').eq('extraction_error', False).execute()
        successful_extractions = successful_result.count

        # Issues with failed extraction
        failed_result = db.table('issues').select('id', count='exact').eq('extraction_error', True).execute()
        failed_extractions = failed_result.count

        # Issues from last 7 days
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_result = db.table('issues').select('id', count='exact').gte('created_at', week_ago).execute()
        recent_issues = recent_result.count

        summary = {
            'total_issues': total_issues or 0,
            'successful_extractions': successful_extractions or 0,
            'failed_extractions': failed_extractions or 0,
            'recent_issues': recent_issues or 0
        }

        return jsonify(summary)

    except Exception as e:
        print(f"Error fetching summary: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@statistics_bp.route('/api/by-type')
@login_required
def get_by_type():
    """Get issues count by type"""
    try:
        db = get_db()

        # Get all issues with their types
        result = db.table('issues').select('issue_type_id, issue_types(name)').execute()
        issues = result.data

        # Count by type
        type_counts = {}
        for issue in issues:
            type_name = issue['issue_types']['name'] if issue.get('issue_types') else 'Unknown'
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        data = {
            'labels': list(type_counts.keys()),
            'data': list(type_counts.values())
        }

        return jsonify(data)

    except Exception as e:
        print(f"Error fetching by-type stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@statistics_bp.route('/api/timeline')
@login_required
def get_timeline():
    """Get issues by type over time based on issue timestamp"""
    try:
        db = get_db()

        # Get all issues with their types and timestamps (use timestamp field, not created_at)
        result = db.table('issues').select('timestamp, issue_type_id, issue_types(name)').order('timestamp').execute()
        issues = result.data

        # Filter out issues without timestamps
        issues = [i for i in issues if i.get('timestamp')]

        if not issues:
            return jsonify({'labels': [], 'datasets': []})

        # Group by month
        monthly_data = {}
        issue_types = set()

        for issue in issues:
            # Extract month from timestamp (YYYY-MM)
            month = issue['timestamp'][:7]
            type_name = issue['issue_types']['name'] if issue.get('issue_types') else 'Unknown'
            issue_types.add(type_name)

            if month not in monthly_data:
                monthly_data[month] = {}

            monthly_data[month][type_name] = monthly_data[month].get(type_name, 0) + 1

        # Sort months chronologically
        sorted_months = sorted(monthly_data.keys())

        # Format labels (e.g., "Jan 2024")
        labels = []
        for month in sorted_months:
            date_obj = datetime.strptime(month, '%Y-%m')
            labels.append(date_obj.strftime('%b %Y'))

        # Create datasets for each issue type
        datasets = []
        for issue_type in sorted(issue_types):
            data = []
            for month in sorted_months:
                count = monthly_data[month].get(issue_type, 0)
                data.append(count)

            datasets.append({
                'label': issue_type,
                'data': data
            })

        return jsonify({
            'labels': labels,
            'datasets': datasets
        })

    except Exception as e:
        print(f"Error fetching timeline: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
