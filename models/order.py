"""
Order and Supplier Models - Procurement Management
"""
from datetime import datetime
from enum import Enum
from .tenant import db


class OrderStatus(Enum):
    DRAFT = 'draft'
    PENDING_APPROVAL = 'pending_approval'
    APPROVED = 'approved'
    SUPPLIER_MATCHING = 'supplier_matching'
    SUPPLIER_CONFIRMED = 'supplier_confirmed'
    PROCESSING = 'processing'
    READY_TO_SHIP = 'ready_to_ship'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'


class CertificationType(Enum):
    GMP = 'GMP'
    FDA = 'FDA'
    ISO_9001 = 'ISO_9001'
    ISO_13485 = 'ISO_13485'
    GDP = 'GDP'
    OTHER = 'other'


class Supplier(db.Model):
    """
    Supplier represents a raw material provider
    with certifications and capabilities.
    """
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    code = db.Column(db.String(50), unique=True)
    
    # Contact
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))
    
    # Address
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100), index=True)
    postal_code = db.Column(db.String(20))
    coordinates = db.Column(db.JSON)  # {lat: x, lng: y}
    
    # Certifications
    certifications = db.Column(db.JSON, default=list)  # ['GMP', 'FDA', 'ISO']
    certification_docs = db.relationship('ComplianceDocument', backref='supplier',
                                          lazy='dynamic', foreign_keys='ComplianceDocument.supplier_id')
    
    # Capabilities
    product_categories = db.Column(db.JSON, default=list)
    temperature_zones = db.Column(db.JSON, default=list)  # ['refrigerated', 'frozen']
    min_order_value = db.Column(db.Float, default=0)
    
    # Performance
    rating = db.Column(db.Float, default=0.0)  # 0-5
    on_time_delivery_rate = db.Column(db.Float, default=0.0)  # 0-100
    quality_score = db.Column(db.Float, default=0.0)  # 0-100
    total_orders = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('OrderItem', backref='supplier', lazy='dynamic')
    
    def __repr__(self):
        return f'<Supplier {self.name}>'
    
    @property
    def reliability_score(self):
        """Calculate overall reliability score"""
        weights = {
            'rating': 0.3,
            'on_time': 0.4,
            'quality': 0.3
        }
        score = (
            (self.rating / 5.0 * 100) * weights['rating'] +
            self.on_time_delivery_rate * weights['on_time'] +
            self.quality_score * weights['quality']
        )
        return min(100, max(0, score))
    
    def calculate_match_score(self, requirements):
        """
        Calculate how well supplier matches requirements
        requirements: {certifications, distance, price_range, temp_zone}
        """
        score = 0
        max_score = 0
        
        # Certification Match (30%)
        if 'certifications' in requirements:
            max_score += 30
            required_certs = set(requirements['certifications'])
            supplier_certs = set(self.certifications or [])
            if required_certs.issubset(supplier_certs):
                score += 30
            else:
                matching = len(required_certs & supplier_certs)
                score += (matching / len(required_certs)) * 30
        
        # Distance Score (20%)
        if 'distance' in requirements:
            max_score += 20
            distance = requirements['distance']
            if distance < 200:
                score += 20
            elif distance < 500:
                score += 15
            elif distance < 1000:
                score += 10
            else:
                score += 5
        
        # Price Competitiveness (20%)
        if 'price_range' in requirements:
            max_score += 20
            # Would compare against market rates
            score += 15  # Placeholder
        
        # Reliability (30%)
        max_score += 30
        score += self.reliability_score * 0.3
        
        return {
            'score': round(score, 1),
            'max_score': max_score,
            'percentage': round((score / max_score * 100) if max_score > 0 else 0, 1)
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'country': self.country,
            'certifications': self.certifications,
            'rating': self.rating,
            'reliability_score': round(self.reliability_score, 1),
            'is_verified': self.is_verified
        }


class Order(db.Model):
    """
    Order represents a procurement request from a tenant
    for raw materials or pharmaceutical products.
    """
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Tenant Relationship
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Order Details
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.DRAFT)
    priority = db.Column(db.String(20), default='standard')
    
    # Requirements
    temperature_zone = db.Column(db.String(50))  # refrigerated, frozen, ultra_cold
    required_certifications = db.Column(db.JSON, default=list)
    delivery_deadline = db.Column(db.DateTime)
    
    # Supplier Assignment
    selected_supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    selected_supplier = db.relationship('Supplier', backref='assigned_orders')
    
    # Financial
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)
    currency = db.Column(db.String(3), default='USD')
    
    # Shipping
    shipping_address = db.Column(db.Text)
    shipping_city = db.Column(db.String(100))
    shipping_country = db.Column(db.String(100))
    
    # Linked Shipment
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'))
    shipment = db.relationship('Shipment', backref='source_order')
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic',
                            cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    @property
    def total_items(self):
        return self.items.count()
    
    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items)
    
    def get_match_scores(self):
        """Get matching scores for all active suppliers"""
        requirements = {
            'certifications': self.required_certifications,
            'temp_zone': self.temperature_zone
        }
        
        suppliers = Supplier.query.filter_by(is_active=True).all()
        scores = []
        
        for supplier in suppliers:
            match = supplier.calculate_match_score(requirements)
            scores.append({
                'supplier': supplier.to_dict(),
                'match_score': match
            })
        
        return sorted(scores, key=lambda x: x['match_score']['percentage'], reverse=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'status': self.status.value,
            'total_items': self.total_items,
            'supplier': self.selected_supplier.to_dict() if self.selected_supplier else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class OrderItem(db.Model):
    """
    Individual item within an order
    """
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    
    # Product Details
    product_name = db.Column(db.String(255), nullable=False)
    product_code = db.Column(db.String(100))
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    
    # Specifications
    grade = db.Column(db.String(50))  # e.g., "Pharma Grade", "GMP Grade"
    purity = db.Column(db.String(50))  # e.g., "98%", "99.5%"
    specifications = db.Column(db.JSON)
    
    # Quantity
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50), default='units')
    
    # Supplier
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    
    # Pricing
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    
    # Status
    status = db.Column(db.String(50), default='pending')
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OrderItem {self.product_name}>'
    
    @property
    def calculated_total(self):
        if self.unit_price and self.quantity:
            return self.unit_price * self.quantity
        return 0
