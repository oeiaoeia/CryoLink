"""
Compliance and Document Management Models
"""
from datetime import datetime
from enum import Enum
import hashlib
import json
from .tenant import db


class DocumentType(Enum):
    CERTIFICATE_OF_ANALYSIS = 'certificate_of_analysis'
    TEMPERATURE_LOG = 'temperature_log'
    CUSTOMS_DECLARATION = 'customs_declaration'
    GDP_CERTIFICATE = 'gdp_certificate'
    CHAIN_OF_CUSTODY = 'chain_of_custody'
    SHIPPING_MANIFEST = 'shipping_manifest'
    REGULATORY_APPROVAL = 'regulatory_approval'
    INSURANCE_CERTIFICATE = 'insurance_certificate'
    OTHER = 'other'


class ComplianceDocument(db.Model):
    """
    Compliance documents for shipments, suppliers, and tenants.
    Includes certificates, logs, declarations, and audit trails.
    """
    __tablename__ = 'compliance_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    document_number = db.Column(db.String(100), unique=True, nullable=False)
    
    # Document Type
    document_type = db.Column(db.Enum(DocumentType), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), index=True)
    
    # File Information
    file_name = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)  # bytes
    mime_type = db.Column(db.String(100))
    
    # Content (for generated documents like temperature logs)
    content = db.Column(db.JSON)
    
    # Issuance
    issued_by = db.Column(db.String(255))  # Organization name
    issued_by_email = db.Column(db.String(255))
    signatory_name = db.Column(db.String(255))
    signatory_title = db.Column(db.String(100))
    
    # Validity
    issued_date = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    is_current = db.Column(db.Boolean, default=True)
    
    # Verification
    verification_status = db.Column(db.String(50), default='pending')  # pending, verified, expired, revoked
    verification_reference = db.Column(db.String(100))  # External verification ID
    blockchain_hash = db.Column(db.String(64))  # SHA-256 hash for immutability
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<ComplianceDocument {self.document_number}>'
    
    @property
    def is_valid(self):
        """Check if document is currently valid"""
        if not self.is_current:
            return False
        if self.valid_until and self.valid_until < datetime.utcnow():
            return False
        return self.verification_status == 'verified'
    
    @property
    def is_expired(self):
        """Check if document is expired"""
        return self.valid_until and self.valid_until < datetime.utcnow()
    
    def generate_blockchain_hash(self):
        """Generate SHA-256 hash for document integrity"""
        data = {
            'document_number': self.document_number,
            'document_type': self.document_type.value,
            'tenant_id': self.tenant_id,
            'shipment_id': self.shipment_id,
            'issued_date': self.issued_date.isoformat() if self.issued_date else None,
            'content': self.content
        }
        json_str = json.dumps(data, sort_keys=True)
        self.blockchain_hash = hashlib.sha256(json_str.encode()).hexdigest()
        return self.blockchain_hash
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_number': self.document_number,
            'document_type': self.document_type.value,
            'title': self.title,
            'document_type_label': self.document_type.value.replace('_', ' ').title(),
            'issued_by': self.issued_by,
            'issued_date': self.issued_date.isoformat() if self.issued_date else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_valid': self.is_valid,
            'is_expired': self.is_expired,
            'verification_status': self.verification_status,
            'blockchain_hash': self.blockchain_hash,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(db.Model):
    """
    Audit trail for compliance tracking.
    Records all significant actions for regulatory compliance.
    """
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Event Details
    event_type = db.Column(db.String(100), nullable=False)
    event_category = db.Column(db.String(50))  # shipment, order, compliance, user, system
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Entity Information
    entity_type = db.Column(db.String(50))  # Shipment, Order, Document, User
    entity_id = db.Column(db.Integer)
    entity_reference = db.Column(db.String(255))  # Human-readable reference
    
    # Tenant Context
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), index=True)
    
    # User Context
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_email = db.Column(db.String(255))
    user_role = db.Column(db.String(50))
    
    # Change Details
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    changes = db.Column(db.JSON)  # Diff of changes
    
    # Context
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    session_id = db.Column(db.String(100))
    
    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditLog {self.event_type} - {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'action': self.action,
            'description': self.description,
            'entity_type': self.entity_type,
            'entity_reference': self.entity_reference,
            'user_email': self.user_email,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
