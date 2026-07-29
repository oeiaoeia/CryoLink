"""
Production Entry Point for Render/Railway
"""
import os
from app import create_app, db
from models import Tenant

# Create app with production config
app = create_app('production')


def ensure_db_initialized():
    """Ensure database is initialized on first run"""
    try:
        with app.app_context():
            # Check if database tables exist
            Tenant.query.first()
    except Exception:
        # Tables don't exist, initialize
        print("Initializing database...")
        try:
            db.create_all()
            print("✓ Database tables created")
            
            # Run seed data
            from init_db import seed_data
            seed_data()
            print("✓ Database seeded")
        except Exception as e:
            print(f"⚠ Database initialization warning: {e}")


# Initialize database on startup (for first deployment)
if os.environ.get('AUTO_INIT_DB', 'false').lower() == 'true':
    ensure_db_initialized()


if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
