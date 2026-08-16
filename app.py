"""
CryoLink - Cold-Chain Supply & Logistics Control Tower
Main Application Entry Point
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import config
from models import db, User, Tenant


# Initialize extensions
login_manager = LoginManager()


def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access CryoLink.'
    login_manager.login_message_category = 'info'
    
    # Prevent caching of authenticated pages
    @app.after_request
    def add_no_cache_headers(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes import auth_bp, dashboard_bp, shipments_bp, orders_bp, compliance_bp, api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(shipments_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(compliance_bp)
    app.register_blueprint(api_bp)
    
    # Root redirect
    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))
    
    # Health check endpoint for Railway
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'CryoLink'}

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        from flask import render_template
        import traceback
        print(f"Unhandled Exception: {error}")
        traceback.print_exc()
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Template context processors
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        from flask import session
        return {
            'current_user': current_user,
            'tenant_name': session.get('tenant_name'),
            'tenant_domain': session.get('tenant_domain')
        }


    # Ensure database tables exist (safe to call even if they already exist)
    with app.app_context():
        try:
            # Drop and recreate tables to fix PostgreSQL enum types
            # Remove this block after first successful deploy
            import os
            if os.environ.get('RESET_DB', 'false').lower() == 'true':
                db.drop_all()
                print("✓ Dropped all tables for fresh start")
            db.create_all()
            print("✓ Database tables ready")
        except Exception as e:
            print(f"⚠ Database table creation note: {e}")

    return app

# Create app instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))


if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5001)
