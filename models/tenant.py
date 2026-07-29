"""
Tenant Model - Multitenant Organization Management
"""
from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TenantStatus(Enum):
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    PENDING = 'pending'
    ARCHIVED = 'archived'


class Tenant(db.Model):
    """
    Tenant represents an organization (pharmaceutical company)
    using the CryoLink platform with complete data isolation.
    """
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    domain = db.Column(db.String(255), unique=True, nullable=False, index=True)
    tenant_id = db.Column(db.String(50), unique=True, nullable=False)  # Short ID for login
    
    # Contact Information
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    country = db.Column(db.String(100))
    
    # Settings
    status = db.Column(db.Enum(TenantStatus), default=TenantStatus.ACTIVE)
    logo_url = db.Column(db.String(500))
    primary_color = db.Column(db.String(20), default='#0066CC')
    timezone = db.Column(db.String(50), default='UTC')
    
    # Compliance
    certifications = db.Column(db.JSON, default=list)  # ['GMP', 'FDA', 'ISO']
    regulatory_approvals = db.Column(db.JSON, default=list)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='tenant', lazy='dynamic', cascade='all, delete-orphan')
    shipments = db.relationship('Shipment', backref='tenant', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='tenant', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('ComplianceDocument', backref='tenant', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tenant {self.name}>'
    
    @property
    def display_name(self):
        return self.name
    
    @property
    def is_active(self):
        return self.status == TenantStatus.ACTIVE
    
    def get_stats(self):
        """Get tenant statistics"""
        from .shipment import ShipmentStatus
        from .order import Order, OrderStatus

        active_shipments = self.shipments.filter_by(status=ShipmentStatus.IN_TRANSIT).count()
        pending_orders = Order.query.filter(
            Order.tenant_id == self.id,
            Order.status.in_([OrderStatus.PENDING_APPROVAL, OrderStatus.DRAFT])
        ).count()
        total_documents = self.documents.count()

        return {
            'active_shipments': active_shipments,
            'pending_orders': pending_orders,
            'total_documents': total_documents
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'tenant_id': self.tenant_id,
            'email': self.email,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
