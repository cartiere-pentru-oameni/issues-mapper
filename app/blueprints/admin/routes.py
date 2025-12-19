from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app.blueprints.admin import admin_bp
from app.utils.auth import admin_required, hash_password
from app.utils.db import get_db


@admin_bp.route('/users')
@admin_required
def users():
    """User management page"""
    try:
        db = get_db()
        result = db.table('users').select('id, email, role, active, created_at').order('created_at', desc=True).execute()
        users = result.data
    except Exception as e:
        flash(f'Error loading users: {str(e)}', 'error')
        users = []

    return render_template('users.html', users=users)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Add new user"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'employee')
        active = request.form.get('active') == 'on'

        # Validate input
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('user_form.html', action='Add', user={'email': email, 'role': role, 'active': active})

        if role not in ['admin', 'employee']:
            flash('Invalid role selected.', 'error')
            return render_template('user_form.html', action='Add', user={'email': email, 'role': role, 'active': active})

        try:
            db = get_db()

            # Check if email already exists
            existing = db.table('users').select('id').eq('email', email).execute()
            if existing.data:
                flash('A user with this email already exists.', 'error')
                return render_template('user_form.html', action='Add', user={'email': email, 'role': role, 'active': active})

            # Create new user
            password_hash = hash_password(password)
            db.table('users').insert({
                'email': email,
                'password_hash': password_hash,
                'role': role,
                'active': active
            }).execute()

            flash('User created successfully!', 'success')
            return redirect(url_for('admin.users'))

        except Exception as e:
            flash(f'Error creating user: {str(e)}', 'error')
            return render_template('user_form.html', action='Add', user={'email': email, 'role': role, 'active': active})

    return render_template('user_form.html', action='Add')


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit existing user"""
    db = None
    try:
        db = get_db()

        # Fetch user from database
        result = db.table('users').select('*').eq('id', user_id).execute()
        if not result.data:
            flash('User not found.', 'error')
            return redirect(url_for('admin.users'))

        user = result.data[0]

        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            role = request.form.get('role', 'employee')
            active = request.form.get('active') == 'on'

            # Validate input
            if not email:
                flash('Email is required.', 'error')
                return render_template('user_form.html', user={'id': user_id, 'email': email, 'role': role, 'active': active}, action='Edit')

            if role not in ['admin', 'employee']:
                flash('Invalid role selected.', 'error')
                return render_template('user_form.html', user={'id': user_id, 'email': email, 'role': role, 'active': active}, action='Edit')

            # Check if email is taken by another user
            existing = db.table('users').select('id').eq('email', email).neq('id', user_id).execute()
            if existing.data:
                flash('A user with this email already exists.', 'error')
                return render_template('user_form.html', user={'id': user_id, 'email': email, 'role': role, 'active': active}, action='Edit')

            # Prevent user from deactivating themselves
            current_user_id = session.get('user_id')
            if user_id == current_user_id and not active:
                flash('You cannot deactivate your own account.', 'error')
                return render_template('user_form.html', user={'id': user_id, 'email': email, 'role': role, 'active': active}, action='Edit')

            # Update user data
            update_data = {
                'email': email,
                'role': role,
                'active': active
            }

            # Only update password if provided
            if password:
                update_data['password_hash'] = hash_password(password)

            db.table('users').update(update_data).eq('id', user_id).execute()

            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.users'))

        return render_template('user_form.html', user=user, action='Edit')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    try:
        # Prevent user from deleting themselves
        current_user_id = session.get('user_id')
        if user_id == current_user_id:
            flash('You cannot delete your own account.', 'error')
            return redirect(url_for('admin.users'))

        db = get_db()

        # Check if user exists
        result = db.table('users').select('id').eq('id', user_id).execute()
        if not result.data:
            flash('User not found.', 'error')
            return redirect(url_for('admin.users'))

        # Delete user
        db.table('users').delete().eq('id', user_id).execute()

        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')

    return redirect(url_for('admin.users'))


@admin_bp.route('/issue-types')
@admin_required
def issue_types():
    """Issue type management page"""
    try:
        db = get_db()
        result = db.table('issue_types').select('id, name, active, created_at').order('name').execute()
        issue_types = result.data
    except Exception as e:
        flash(f'Error loading issue types: {str(e)}', 'error')
        issue_types = []

    return render_template('issue_types.html', issue_types=issue_types)


@admin_bp.route('/issue-types/add', methods=['GET', 'POST'])
@admin_required
def add_issue_type():
    """Add new issue type"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        active = request.form.get('active') == 'on'

        # Validate input
        if not name:
            flash('Name is required.', 'error')
            return render_template('issue_type_form.html', action='Add', issue_type={'name': name, 'active': active})

        try:
            db = get_db()

            # Check if name already exists
            existing = db.table('issue_types').select('id').eq('name', name).execute()
            if existing.data:
                flash('An issue type with this name already exists.', 'error')
                return render_template('issue_type_form.html', action='Add', issue_type={'name': name, 'active': active})

            # Create new issue type
            db.table('issue_types').insert({
                'name': name,
                'active': active
            }).execute()

            flash('Issue type created successfully!', 'success')
            return redirect(url_for('admin.issue_types'))

        except Exception as e:
            flash(f'Error creating issue type: {str(e)}', 'error')
            return render_template('issue_type_form.html', action='Add', issue_type={'name': name, 'active': active})

    return render_template('issue_type_form.html', action='Add')


@admin_bp.route('/issue-types/<int:type_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_issue_type(type_id):
    """Edit existing issue type"""
    try:
        db = get_db()

        # Fetch issue type from database
        result = db.table('issue_types').select('*').eq('id', type_id).execute()
        if not result.data:
            flash('Issue type not found.', 'error')
            return redirect(url_for('admin.issue_types'))

        issue_type = result.data[0]

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            active = request.form.get('active') == 'on'

            # Validate input
            if not name:
                flash('Name is required.', 'error')
                return render_template('issue_type_form.html', issue_type={'id': type_id, 'name': name, 'active': active}, action='Edit')

            # Check if name is taken by another issue type
            existing = db.table('issue_types').select('id').eq('name', name).neq('id', type_id).execute()
            if existing.data:
                flash('An issue type with this name already exists.', 'error')
                return render_template('issue_type_form.html', issue_type={'id': type_id, 'name': name, 'active': active}, action='Edit')

            # Update issue type data
            db.table('issue_types').update({
                'name': name,
                'active': active
            }).eq('id', type_id).execute()

            flash('Issue type updated successfully!', 'success')
            return redirect(url_for('admin.issue_types'))

        return render_template('issue_type_form.html', issue_type=issue_type, action='Edit')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin.issue_types'))


@admin_bp.route('/issue-types/<int:type_id>/delete', methods=['POST'])
@admin_required
def delete_issue_type(type_id):
    """Delete issue type"""
    try:
        db = get_db()

        # Check if issue type exists
        result = db.table('issue_types').select('id').eq('id', type_id).execute()
        if not result.data:
            flash('Issue type not found.', 'error')
            return redirect(url_for('admin.issue_types'))

        # Check if issue type is used by any issues
        issues_using_type = db.table('issues').select('id', count='exact').eq('issue_type_id', type_id).execute()
        if issues_using_type.count > 0:
            flash(f'Cannot delete issue type. It is used by {issues_using_type.count} issue(s).', 'error')
            return redirect(url_for('admin.issue_types'))

        # Delete issue type
        db.table('issue_types').delete().eq('id', type_id).execute()

        flash('Issue type deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting issue type: {str(e)}', 'error')

    return redirect(url_for('admin.issue_types'))
