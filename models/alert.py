"""
Alert and Notification Models
"""
from datetime import datetime
from enum import Enum
from .tenant import db


class AlertType(Enum):
    TEMPERATURE_EXCURSION = 'temperature_excursion'
    DELAY_RISK = 'delay_risk'
    CUSTOMS_ISSUE = 'customs_issue'
    ROUTE_CHANGE = 'route_change'
    DOCUMENT_EXPIRING = 'document_expiring'
    SHIPMENT_EXCEPTION = 'shipment_exception'
    SYSTEM_ALERT = 'system_alert'
    MAINTENANCE = 'maintenance'
    COMPLIANCE_REMINDER = 'compliance_reminder'


class AlertSeverity(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class AlertStatus(Enum):
    NEW = 'new'
    ACKNOWLEDGED = 'acknowledged'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    CLOSED = 'closed'
    FALSE_ALARM = 'false_alarm'


class Alert(db.Model):
    """
    Alerts for temperature excursions, delays, compliance issues,
    and other events requiring attention.
    """
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Alert Type
    alert_type = db.Column(db.Enum(AlertType), nullable=False)
    severity = db.Column(db.Enum(AlertSeverity), default=AlertSeverity.MEDIUM)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Context
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), index=True)
    
    # Status
    status = db.Column(db.Enum(AlertStatus), default=AlertStatus.NEW)
    
    # Timing
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Assignment
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_alert_assigned_to'))
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_alert_acknowledged_by'))
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_alert_resolved_by'))
    
    # Details
    location = db.Column(db.String(255))
    current_value = db.Column(db.String(100))  # e.g., current temperature
    threshold_value = db.Column(db.String(100))  # e.g., acceptable range
    
    # Suggested Actions
    suggested_actions = db.Column(db.JSON, default=list)
    auto_actions_taken = db.Column(db.JSON, default=list)
    
    # Resolution
    resolution_notes = db.Column(db.Text)
    root_cause = db.Column(db.String(255))
    preventive_measure = db.Column(db.Text)
    
    # Notifications
    notifications_sent = db.Column(db.JSON, default=list)
    escalation_level = db.Column(db.Integer, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Alert {self.alert_number} - {self.alert_type.value}>'
    
    @property
    def is_active(self):
        return self.status in [AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.IN_PROGRESS]
    
    @property
    def is_critical(self):
        return self.severity == AlertSeverity.CRITICAL
    
    @property
    def requires_immediate_action(self):
        """Check if alert requires immediate action"""
        return (
            self.is_critical or
            (self.alert_type == AlertType.TEMPERATURE_EXCURSION and self.is_active)
        )
    
    def acknowledge(self, user_id):
        """Acknowledge the alert"""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = user_id
    
    def resolve(self, user_id, notes=None):
        """Resolve the alert"""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        if notes:
            self.resolution_notes = notes
    
    def get_color(self):
        """Get alert color based on severity"""
        colors = {
            AlertSeverity.LOW: '#00C853',
            AlertSeverity.MEDIUM: '#FFB300',
            AlertSeverity.HIGH: '#FF5722',
            AlertSeverity.CRITICAL: '#D32F2F'
        }
        return colors.get(self.severity, '#757575')
    
    def get_icon(self):
        """Get alert icon based on type"""
        icons = {
            AlertType.TEMPERATURE_EXCURSION: '🌡️',
            AlertType.DELAY_RISK: '⏱️',
            AlertType.CUSTOMS_ISSUE: '🛃',
            AlertType.ROUTE_CHANGE: '🔄',
            AlertType.DOCUMENT_EXPIRING: '📄',
            AlertType.SHIPMENT_EXCEPTION: '⚠️',
            AlertType.SYSTEM_ALERT: '🔔',
            AlertType.MAINTENANCE: '🔧',
            AlertType.COMPLIANCE_REMINDER: '📋'
        }
        return icons.get(self.alert_type, '📢')
    
    def to_dict(self):
        return {
            'id': self.id,
            'alert_number': self.alert_number,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'status': self.status.value,
            'shipment_id': self.shipment_id,
            'location': self.location,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'suggested_actions': self.suggested_actions,
            'color': self.get_color(),
            'icon': self.get_icon()
        }


class AlertAction(db.Model):
    """
    Actions taken in response to alerts
    """
    __tablename__ = 'alert_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.id'), nullable=False)
    
    # Action Details
    action_type = db.Column(db.String(100), nullable=False)
    action_description = db.Column(db.Text)
    
    # Execution
    executed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_automated = db.Column(db.Boolean, default=False)
    
    # Result
    result_status = db.Column(db.String(50), default='pending')  # pending, success, failed
    result_message = db.Column(db.Text)
    
    # Related Entities
    target_facility = db.Column(db.String(255))
    target_contact = db.Column(db.String(255))
    reference_number = db.Column(db.String(100))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    alert = db.relationship('Alert', backref='actions')
    
    def __repr__(self):
        return f'<AlertAction {self.action_type} for Alert {self.alert_id}>'
