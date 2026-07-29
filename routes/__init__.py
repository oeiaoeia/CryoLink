"""
Routes Package
"""
from .auth import auth_bp
from .dashboard import dashboard_bp
from .shipments import shipments_bp
from .orders import orders_bp
from .compliance import compliance_bp
from .api import api_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'shipments_bp',
    'orders_bp',
    'compliance_bp',
    'api_bp'
]
