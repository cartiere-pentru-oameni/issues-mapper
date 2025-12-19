from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app.blueprints.issues import issues_bp
from app.utils.auth import login_required
from app.utils.db import get_db
import csv
from io import StringIO


@issues_bp.route('/')
@login_required
def index():
    """Tabular view with sortable columns and filtering"""
    return render_template('issues/issues_list.html')


@issues_bp.route('/api/list')
@login_required
def get_issues():
    """API endpoint for datatable - supports sorting, filtering, pagination"""
    try:
        db = get_db()

        # Fetch all issues with their type names
        query = db.table('issues').select('id, latitude, longitude, timestamp, image_url, extraction_error, issue_types(name)')

        # Order by newest first
        query = query.order('created_at', desc=True)

        result = query.execute()
        issues_data = result.data

        # Format data for datatable
        formatted_issues = []
        for issue in issues_data:
            formatted_issues.append({
                'id': issue['id'],
                'type': issue['issue_types']['name'] if issue.get('issue_types') else 'Unknown',
                'latitude': issue['latitude'],
                'longitude': issue['longitude'],
                'timestamp': issue['timestamp'],
                'extraction_error': issue['extraction_error'],
                'image_url': issue['image_url']
            })

        return jsonify({
            'draw': request.args.get('draw', type=int, default=1),
            'recordsTotal': len(formatted_issues),
            'recordsFiltered': len(formatted_issues),
            'data': formatted_issues
        })

    except Exception as e:
        print(f"Error fetching issues list: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@issues_bp.route('/<int:issue_id>')
@login_required
def detail(issue_id):
    """Issue detail view for editing and deleting"""
    try:
        db = get_db()

        # Fetch issue with type name
        result = db.table('issues').select('*, issue_types(name)').eq('id', issue_id).execute()

        if not result.data:
            flash('Issue not found', 'error')
            return redirect(url_for('issues.index'))

        issue = result.data[0]
        issue['type'] = issue['issue_types']['name'] if issue.get('issue_types') else 'Unknown'

        return render_template('issues/issue_detail.html', issue=issue)

    except Exception as e:
        print(f"Error fetching issue detail: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading issue details', 'error')
        return redirect(url_for('issues.index'))


@issues_bp.route('/<int:issue_id>/delete', methods=['POST'])
@login_required
def delete(issue_id):
    """Delete an issue"""
    try:
        db = get_db()

        # Delete the issue
        db.table('issues').delete().eq('id', issue_id).execute()

        flash('Issue deleted successfully!', 'success')
        return redirect(url_for('issues.index'))

    except Exception as e:
        print(f"Error deleting issue: {e}")
        import traceback
        traceback.print_exc()
        flash('Error deleting issue', 'error')
        return redirect(url_for('issues.detail', issue_id=issue_id))


@issues_bp.route('/export')
@login_required
def export():
    """Export issues to CSV"""
    try:
        db = get_db()

        # Fetch all issues
        result = db.table('issues').select('id, latitude, longitude, timestamp, issue_types(name)').order('created_at', desc=True).execute()
        issues_data = result.data

        # Format for CSV
        csv_data = []
        for issue in issues_data:
            csv_data.append({
                'id': issue['id'],
                'type': issue['issue_types']['name'] if issue.get('issue_types') else 'Unknown',
                'latitude': issue['latitude'],
                'longitude': issue['longitude'],
                'timestamp': issue['timestamp']
            })

        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=['id', 'type', 'latitude', 'longitude', 'timestamp'])
        writer.writeheader()
        writer.writerows(csv_data)

        # Create response
        from flask import make_response
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=issues_export.csv'
        response.headers['Content-Type'] = 'text/csv'

        return response

    except Exception as e:
        print(f"Error exporting issues: {e}")
        import traceback
        traceback.print_exc()
        flash('Error exporting issues', 'error')
        return redirect(url_for('issues.index'))
