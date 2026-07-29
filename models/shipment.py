"""
Shipment Models - Tracking and Route Management
"""
from datetime import datetime
from enum import Enum
from .tenant import db
from .temperature import TemperatureLog


class ShipmentStatus(Enum):
    DRAFT = 'draft'
    SCHEDULED = 'scheduled'
    IN_TRANSIT = 'in_transit'
    DELAYED = 'delayed'
    CUSTOMS_HOLD = 'customs_hold'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    EXCEPTION = 'exception'


class TransportMode(Enum):
    AIR = 'air'
    SEA = 'sea'
    ROAD = 'road'
    RAIL = 'rail'


class Shipment(db.Model):
    """
    Shipment represents a cold-chain logistics shipment
    with temperature requirements and route tracking.
    """
    __tablename__ = 'shipments'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Tenant Relationship
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Product Information
    product_name = db.Column(db.String(255), nullable=False)
    product_type = db.Column(db.String(100))  # Vaccine, Biologic, Raw Material, etc.
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50), default='units')  # kg, liters, units, etc.
    
    # Temperature Requirements
    temp_zone = db.Column(db.String(50), nullable=False)  # refrigerated, frozen, ultra_cold
    temp_min = db.Column(db.Float, nullable=False)
    temp_max = db.Column(db.Float, nullable=False)
    thermal_buffer_minutes = db.Column(db.Integer, default=30)  # Time before product compromised
    
    # Route Information
    origin_city = db.Column(db.String(100), nullable=False)
    origin_country = db.Column(db.String(100), nullable=False)
    origin_facility = db.Column(db.String(255))
    
    destination_city = db.Column(db.String(100), nullable=False)
    destination_country = db.Column(db.String(100), nullable=False)
    destination_facility = db.Column(db.String(255))
    
    # Status & Tracking
    status = db.Column(db.Enum(ShipmentStatus), default=ShipmentStatus.DRAFT)
    priority = db.Column(db.String(20), default='standard')  # urgent, standard, economy
    
    # Timing
    scheduled_departure = db.Column(db.DateTime)
    estimated_arrival = db.Column(db.DateTime)
    actual_departure = db.Column(db.DateTime)
    actual_arrival = db.Column(db.DateTime)
    
    # Progress
    progress_percentage = db.Column(db.Float, default=0.0)
    current_location = db.Column(db.String(255))
    current_coordinates = db.Column(db.JSON)  # {lat: x, lng: y}
    
    # Risk & Quality
    risk_score = db.Column(db.Integer, default=0)  # 0-100
    integrity_score = db.Column(db.Integer, default=100)  # 0-100
    delay_probability = db.Column(db.Integer, default=0)  # 0-100
    
    # Carrier Information
    carrier_name = db.Column(db.String(255))
    carrier_reference = db.Column(db.String(100))
    tracking_number = db.Column(db.String(100))
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    route = db.relationship('Route', backref='shipment', uselist=False, cascade='all, delete-orphan')
    temperature_logs = db.relationship('TemperatureLog', backref='shipment', lazy='dynamic',
                                        cascade='all, delete-orphan')
    excursions = db.relationship('TemperatureExcursion', backref='shipment', lazy='dynamic',
                                  cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='shipment', lazy='dynamic',
                             cascade='all, delete-orphan')
    documents = db.relationship('ComplianceDocument', backref='shipment', lazy='dynamic',
                                cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Shipment {self.shipment_number}>'
    
    @property
    def is_active(self):
        return self.status in [ShipmentStatus.IN_TRANSIT, ShipmentStatus.DELAYED,
                               ShipmentStatus.CUSTOMS_HOLD, ShipmentStatus.EXCEPTION]
    
    @property
    def temp_range_label(self):
        return f"{self.temp_min}°C to {self.temp_max}°C"
    
    @property
    def eta_remaining(self):
        """Get remaining time until ETA"""
        if self.estimated_arrival and self.status == ShipmentStatus.IN_TRANSIT:
            delta = self.estimated_arrival - datetime.utcnow()
            return delta
        return None
    
    @property
    def risk_level(self):
        """Get risk level based on score"""
        if self.risk_score <= 30:
            return 'low'
        elif self.risk_score <= 60:
            return 'moderate'
        else:
            return 'high'
    
    @property
    def integrity_level(self):
        """Get integrity level"""
        if self.integrity_score >= 90:
            return 'excellent'
        elif self.integrity_score >= 70:
            return 'good'
        elif self.integrity_score >= 50:
            return 'fair'
        else:
            return 'poor'
    
    def get_current_temperature(self):
        """Get latest temperature reading"""
        latest = self.temperature_logs.order_by(
            TemperatureLog.timestamp.desc()
        ).first()
        return latest.temperature if latest else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'shipment_number': self.shipment_number,
            'product_name': self.product_name,
            'status': self.status.value,
            'temp_zone': self.temp_zone,
            'temp_min': self.temp_min,
            'temp_max': self.temp_max,
            'origin': f"{self.origin_city}, {self.origin_country}",
            'destination': f"{self.destination_city}, {self.destination_country}",
            'current_temperature': self.get_current_temperature(),
            'risk_score': self.risk_score,
            'integrity_score': self.integrity_score,
            'progress_percentage': self.progress_percentage,
            'eta': self.estimated_arrival.isoformat() if self.estimated_arrival else None
        }


class Route(db.Model):
    """
    Route defines the planned path for a shipment
    with multiple legs and transport modes.
    """
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False)
    
    # Route Selection
    route_type = db.Column(db.String(50))  # air_express, sea_freight, hybrid
    is_selected = db.Column(db.Boolean, default=False)
    
    # Metrics
    total_distance_km = db.Column(db.Float)
    total_duration_hours = db.Column(db.Float)
    estimated_cost = db.Column(db.Float)
    co2_emissions_kg = db.Column(db.Float)
    risk_score = db.Column(db.Integer, default=0)
    
    # Legs
    legs = db.relationship('RouteLeg', backref='route', lazy='dynamic',
                           cascade='all, delete-orphan', order_by='RouteLeg.sequence')
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Route {self.id} for Shipment {self.shipment_id}>'
    
    @property
    def risk_level(self):
        if self.risk_score <= 30:
            return 'low'
        elif self.risk_score <= 60:
            return 'moderate'
        else:
            return 'high'


class RouteLeg(db.Model):
    """
    Individual segment of a route (e.g., origin pickup, air freight, customs)
    """
    __tablename__ = 'route_legs'
    
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    
    # Leg Details
    name = db.Column(db.String(255), nullable=False)  # e.g., "Origin Pickup", "Tokyo Transit"
    location = db.Column(db.String(255))
    coordinates = db.Column(db.JSON)  # {lat: x, lng: y}
    
    # Transport
    transport_mode = db.Column(db.Enum(TransportMode))
    carrier = db.Column(db.String(255))
    vehicle_reference = db.Column(db.String(100))  # Flight number, vessel name, truck ID
    
    # Timing
    estimated_duration_hours = db.Column(db.Float)
    scheduled_start = db.Column(db.DateTime)
    scheduled_end = db.Column(db.DateTime)
    actual_start = db.Column(db.DateTime)
    actual_end = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, delayed
    temp_risk = db.Column(db.String(20), default='low')  # low, medium, high
    customs_status = db.Column(db.String(50))  # N/A, pre_cleared, automated, pending
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RouteLeg {self.sequence}: {self.name}>'
