"""
Temperature Monitoring Models
"""
from datetime import datetime
from .tenant import db


class TemperatureLog(db.Model):
    """
    Temperature readings from IoT sensors during shipment.
    Recorded at regular intervals for compliance and monitoring.
    """
    __tablename__ = 'temperature_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False, index=True)
    
    # Reading
    temperature = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), default='celsius')
    
    # Location Context
    location = db.Column(db.String(255))
    coordinates = db.Column(db.JSON)  # {lat: x, lng: y}
    
    # Sensor Data
    sensor_id = db.Column(db.String(100))
    sensor_type = db.Column(db.String(50))  # ambient, product, container
    
    # Reading Context
    journey_stage = db.Column(db.String(100))  # origin_pickup, in_transit, customs, etc.
    transport_mode = db.Column(db.String(50))
    
    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TemperatureLog {self.shipment_id} - {self.temperature}°C @ {self.timestamp}>'
    
    @property
    def is_within_range(self):
        """Check if temperature is within acceptable range"""
        if self.shipment:
            return (self.shipment.temp_min <= self.temperature <= self.shipment.temp_max)
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'shipment_id': self.shipment_id,
            'temperature': self.temperature,
            'unit': self.unit,
            'location': self.location,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_within_range': self.is_within_range
        }


class TemperatureExcursion(db.Model):
    """
    Records temperature excursion events when product
    goes outside acceptable temperature range.
    """
    __tablename__ = 'temperature_excursions'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False, index=True)
    
    # Excursion Details
    excursion_type = db.Column(db.String(50), nullable=False)  # high_temp, low_temp, prolonged
    
    # Temperature Data
    min_temperature = db.Column(db.Float)
    max_temperature = db.Column(db.Float)
    threshold_min = db.Column(db.Float)
    threshold_max = db.Column(db.Float)
    
    # Timing
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    
    # Impact Assessment
    severity = db.Column(db.String(20), default='low')  # low, moderate, high, critical
    product_impact = db.Column(db.String(20))  # none, minimal, moderate, compromised
    potency_loss_estimate = db.Column(db.Float)  # percentage
    
    # Location
    location = db.Column(db.String(255))
    journey_stage = db.Column(db.String(100))
    
    # Response
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    response_action = db.Column(db.Text)
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(50), default='open')  # open, investigating, resolved, closed
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TemperatureExcursion {self.shipment_id} - {self.excursion_type}>'
    
    @property
    def is_resolved(self):
        return self.status in ['resolved', 'closed']
    
    @property
    def is_critical(self):
        return self.severity in ['high', 'critical']
    
    def calculate_duration(self):
        """Calculate excursion duration in minutes"""
        if self.started_at and self.ended_at:
            delta = self.ended_at - self.started_at
            return int(delta.total_seconds() / 60)
        elif self.started_at:
            delta = datetime.utcnow() - self.started_at
            return int(delta.total_seconds() / 60)
        return 0
    
    def assess_impact(self):
        """Assess product impact based on excursion parameters"""
        if not self.shipment:
            return
        
        duration = self.calculate_duration()
        buffer = self.shipment.thermal_buffer_minutes or 30
        
        # Calculate how much buffer was exceeded
        if duration <= buffer * 0.5:
            self.product_impact = 'none'
            self.severity = 'low'
            self.potency_loss_estimate = 0.0
        elif duration <= buffer:
            self.product_impact = 'minimal'
            self.severity = 'moderate'
            self.potency_loss_estimate = min(2.0, (duration / buffer) * 2)
        elif duration <= buffer * 1.5:
            self.product_impact = 'moderate'
            self.severity = 'high'
            self.potency_loss_estimate = min(10.0, (duration / buffer) * 5)
        else:
            self.product_impact = 'compromised'
            self.severity = 'critical'
            self.potency_loss_estimate = min(50.0, (duration / buffer) * 10)
    
    def to_dict(self):
        return {
            'id': self.id,
            'shipment_id': self.shipment_id,
            'excursion_type': self.excursion_type,
            'severity': self.severity,
            'duration_minutes': self.duration_minutes or self.calculate_duration(),
            'max_temperature': self.max_temperature,
            'min_temperature': self.min_temperature,
            'product_impact': self.product_impact,
            'potency_loss_estimate': self.potency_loss_estimate,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'location': self.location
        }
