"""
Authentication Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Tenant, TenantStatus, UserStatus
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with tenant selection"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        tenant_domain = request.form.get('tenant_domain', '').strip().lower()
        remember = request.form.get('remember', False)

        # Find user
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Invalid email or password.', 'error')
            return render_template('auth/login.html')

        # Verify password first
        if not user.check_password(password):
            user.login_attempts += 1
            from app import db
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
            flash('Invalid email or password.', 'error')
            return render_template('auth/login.html')

        # Check account status
        if user.status != UserStatus.ACTIVE:
            flash('Your account is not active. Please contact support.', 'error')
            return render_template('auth/login.html')

        # Login successful
        login_user(user, remember=remember)
        user.login_attempts = 0
        user.last_login = datetime.utcnow()

        # Store tenant info in session
        if user.tenant:
            session['tenant_id'] = user.tenant.id
            session['tenant_name'] = user.tenant.name
            session['tenant_domain'] = user.tenant.domain
        elif user.is_super_admin or user.is_operations_admin:
            # Admin users can access all tenants
            session['tenant_id'] = None
            session['tenant_name'] = 'Operations'
            session['tenant_domain'] = 'cryolink.com'

        from app import db
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Login error, please try again.', 'error')
            return render_template('auth/login.html')

        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    # Get popular tenants for quick select
    popular_tenants = Tenant.query.filter_by(status=TenantStatus.ACTIVE).limit(6).all()
    return render_template('auth/login.html', tenants=popular_tenants)


@auth_bp.route('/logout')
def logout():
    """User logout"""
    from flask_login import logout_user
    from flask import session, redirect, url_for, flash, make_response
    
    # Force logout (including remember me cookie)
    logout_user()
    
    # Clear all session data
    session.clear()
    
    # Set flash message
    flash('You have been logged out successfully.', 'info')
    
    # Create response with redirect
    response = make_response(redirect(url_for('auth.login')))
    
    # Clear all cookies related to authentication
    response.set_cookie('remember_token', '', expires=0, path='/')
    response.set_cookie('session', '', expires=0, path='/')
    
    return response


@auth_bp.route('/select-tenant', methods=['GET', 'POST'])
@login_required
def select_tenant():
    """Allow users with multiple tenants to select context"""
    if request.method == 'POST':
        tenant_id = request.form.get('tenant_id')
        tenant = Tenant.query.get(tenant_id)
        
        if tenant and current_user.can_access_tenant(tenant.id):
            session['tenant_id'] = tenant.id
            session['tenant_name'] = tenant.name
            return redirect(url_for('dashboard.index'))
        flash('Invalid tenant selection.', 'error')
    
    # Get accessible tenants
    if current_user.is_super_admin or current_user.is_operations_admin:
        tenants = Tenant.query.filter_by(status=TenantStatus.ACTIVE).all()
    else:
        tenants = [current_user.tenant] if current_user.tenant else []
    
    return render_template('auth/select_tenant.html', tenants=tenants)


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile view"""
    return render_template('auth/profile.html')


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        job_title = request.form.get('job_title')
        timezone = request.form.get('timezone')
        
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.phone = phone
        current_user.job_title = job_title
        current_user.timezone = timezone
        
        from app import db
        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile.', 'error')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('auth.profile'))
    
    if len(new_password) < 8:
        flash('Password must be at least 8 characters long.', 'error')
        return redirect(url_for('auth.profile'))
    
    current_user.set_password(new_password)
    from app import db
    try:
        db.session.commit()
        flash('Password changed successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error changing password.', 'error')

    return redirect(url_for('auth.profile'))
