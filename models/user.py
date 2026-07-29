"""
User Model - Authentication and Authorization
"""
from datetime import datetime
from enum import Enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .tenant import db


class UserRole(Enum):
    SUPER_ADMIN = 'super_admin'  # CryoLink internal
    OPERATIONS_ADMIN = 'operations_admin'  # CryoLink operations
    TENANT_ADMIN = 'tenant_admin'  # Tenant organization admin
    LOGISTICS_COORDINATOR = 'logistics_coordinator'
    PROCUREMENT_MANAGER = 'procurement_manager'
    VIEWER = 'viewer'


class UserStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    PENDING_VERIFICATION = 'pending_verification'


class User(UserMixin, db.Model):
    """
    User model for authentication and authorization.
    Users belong to a tenant (except super admins).
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50))
    job_title = db.Column(db.String(100))
    department = db.Column(db.String(100))
    
    # Authorization
    role = db.Column(db.Enum(UserRole), default=UserRole.VIEWER)
    status = db.Column(db.Enum(UserStatus), default=UserStatus.PENDING_VERIFICATION)
    
    # Tenant Relationship
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)
    
    # Settings
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='en')
    notifications_enabled = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    
    # Security
    last_login = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    password_changed_at = db.Column(db.DateTime)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_shipments = db.relationship('Shipment', backref='creator', lazy='dynamic',
                                         foreign_keys='Shipment.created_by')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        return self.full_name
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        self.password_changed_at = datetime.utcnow()
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_active(self):
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_authenticated(self):
        return self.status == UserStatus.ACTIVE and (
            self.locked_until is None or self.locked_until < datetime.utcnow()
        )
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_super_admin(self):
        return self.role == UserRole.SUPER_ADMIN
    
    @property
    def is_operations_admin(self):
        return self.role == UserRole.OPERATIONS_ADMIN
    
    @property
    def is_tenant_admin(self):
        return self.role == UserRole.TENANT_ADMIN
    
    def can_access_tenant(self, tenant_id):
        """Check if user can access tenant data"""
        if self.is_super_admin or self.is_operations_admin:
            return True
        return self.tenant_id == tenant_id
    
    def get_permissions(self):
        """Get user permissions based on role"""
        permissions = {
            UserRole.SUPER_ADMIN: ['all'],
            UserRole.OPERATIONS_ADMIN: ['view_all_tenants', 'manage_carriers', 
                                        'view_global_dashboard', 'manage_risks'],
            UserRole.TENANT_ADMIN: ['manage_users', 'view_all_shipments', 
                                    'create_orders', 'export_compliance'],
            UserRole.LOGISTICS_COORDINATOR: ['create_shipments', 'track_shipments',
                                              'view_documents'],
            UserRole.PROCUREMENT_MANAGER: ['create_orders', 'manage_suppliers',
                                           'view_shipments'],
            UserRole.VIEWER: ['view_shipments', 'view_documents']
        }
        return permissions.get(self.role, [])
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        permissions = self.get_permissions()
        return 'all' in permissions or permission in permissions
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role.value,
            'tenant_id': self.tenant_id,
            'tenant_name': self.tenant.name if self.tenant else None,
            'status': self.status.value
        }
