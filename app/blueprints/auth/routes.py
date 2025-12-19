from flask import render_template, request, redirect, url_for, flash, session
from app.blueprints.auth import auth_bp
from app.utils.db import get_db
from app.utils.auth import hash_password, verify_password


def check_if_setup_needed():
    """Check if any users exist in the database"""
    try:
        db = get_db()
        result = db.table('users').select('id', count='exact').execute()
        return result.count == 0
    except Exception as e:
        # If table doesn't exist yet, setup is needed
        return True


@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    """First-time setup - create initial admin user"""
    # Check if setup is needed
    if not check_if_setup_needed():
        flash('Setup has already been completed.', 'info')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('setup.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('setup.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('setup.html')

        try:
            # Create admin user
            db = get_db()
            password_hash = hash_password(password)

            result = db.table('users').insert({
                'email': email,
                'password_hash': password_hash,
                'role': 'admin',
                'active': True
            }).execute()

            flash('Admin account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f'Error creating admin account: {str(e)}', 'error')
            return render_template('setup.html')

    return render_template('setup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Check if setup is needed
    if check_if_setup_needed():
        return redirect(url_for('auth.setup'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')

        try:
            # Query user from database
            db = get_db()
            result = db.table('users').select('id, email, password_hash, role, active').eq('email', email).execute()

            if result.data and len(result.data) > 0:
                user = result.data[0]

                if verify_password(user['password_hash'], password):
                    if not user['active']:
                        flash('Your account is inactive. Please contact an administrator.', 'error')
                        return render_template('login.html')

                    # Set session
                    session['user_id'] = user['id']
                    session['user_email'] = user['email']
                    session['user_role'] = user['role']

                    flash('Login successful!', 'success')
                    return redirect(url_for('upload.index'))
                else:
                    flash('Invalid email or password.', 'error')
                    return render_template('login.html')
            else:
                flash('Invalid email or password.', 'error')
                return render_template('login.html')

        except Exception as e:
            flash(f'Error during login: {str(e)}', 'error')
            return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
