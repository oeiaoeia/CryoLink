"""
Dashboard Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app, request
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta
from models import (
    db, Tenant, TenantStatus, User, Shipment, ShipmentStatus, Order, OrderStatus,
    Alert, AlertStatus, AlertSeverity, TemperatureLog, ComplianceDocument
)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard - redirects based on user role"""
    if current_user.is_super_admin or current_user.is_operations_admin:
        return redirect(url_for('dashboard.operations'))
    else:
        return redirect(url_for('dashboard.tenant'))


@dashboard_bp.route('/operations')
@login_required
def operations():
    """Operations Control Tower - Internal Admin Dashboard"""
    if not (current_user.is_super_admin or current_user.is_operations_admin):
        flash('Access denied. Operations dashboard is for internal staff only.', 'error')
        return redirect(url_for('dashboard.tenant'))
    
    # Global Statistics
    total_tenants = Tenant.query.filter_by(status='active').count()
    total_shipments = Shipment.query.count()
    active_shipments = Shipment.query.filter_by(status=ShipmentStatus.IN_TRANSIT).count()
    
    # Alert Summary
    critical_alerts = Alert.query.filter(
        Alert.severity == AlertSeverity.CRITICAL,
        Alert.status == AlertStatus.NEW
    ).count()
    
    active_alerts = Alert.query.filter(
        Alert.status.in_([AlertStatus.NEW, AlertStatus.ACKNOWLEDGED])
    ).count()
    
    # Shipments by Status
    shipments_by_status = db.session.query(
        Shipment.status, func.count(Shipment.id)
    ).group_by(Shipment.status).all()
    
    # Recent Alerts
    recent_alerts = Alert.query.order_by(Alert.created_at.desc()).limit(5).all()
    
    # Tenant Overview
    tenants = Tenant.query.filter(Tenant.status == TenantStatus.ACTIVE).all()
    tenant_stats = []
    for tenant in tenants:
        stats = tenant.get_stats()
        tenant_stats.append({
            'tenant': tenant,
            'stats': stats
        })
    
    # Global Map Data (active shipments with coordinates)
    map_shipments = Shipment.query.filter(
        Shipment.status == ShipmentStatus.IN_TRANSIT,
        Shipment.current_coordinates.isnot(None)
    ).limit(50).all()
    
    # Carrier Performance (placeholder)
    carrier_performance = 94  # Would calculate from historical data
    
    return render_template('dashboard/operations.html',
                         total_tenants=total_tenants,
                         total_shipments=total_shipments,
                         active_shipments=active_shipments,
                         critical_alerts=critical_alerts,
                         active_alerts=active_alerts,
                         shipments_by_status=shipments_by_status,
                         recent_alerts=recent_alerts,
                         tenant_stats=tenant_stats,
                         map_shipments=map_shipments,
                         carrier_performance=carrier_performance)


@dashboard_bp.route('/tenant')
@login_required
def tenant():
    """Tenant Dashboard - Client View"""
    if not current_user.tenant:
        flash('No tenant associated with your account.', 'error')
        return redirect(url_for('auth.select_tenant'))
    
    tenant_id = session.get('tenant_id', current_user.tenant.id)
    tenant = Tenant.query.get(tenant_id)
    
    if not tenant or not current_user.can_access_tenant(tenant.id):
        flash('Access denied to this tenant.', 'error')
        return redirect(url_for('auth.select_tenant'))
    
    # Shipment Statistics
    active_shipments = Shipment.query.filter_by(
        tenant_id=tenant.id,
        status=ShipmentStatus.IN_TRANSIT
    ).count()
    
    pending_orders = Order.query.filter_by(
        tenant_id=tenant.id,
        status=OrderStatus.PENDING_APPROVAL
    ).count()
    
    # Recent Shipments
    recent_shipments = Shipment.query.filter_by(
        tenant_id=tenant.id
    ).order_by(Shipment.created_at.desc()).limit(5).all()
    
    # Compliance Status
    total_documents = ComplianceDocument.query.filter_by(
        tenant_id=tenant.id,
        is_current=True
    ).count()
    
    valid_documents = ComplianceDocument.query.filter_by(
        tenant_id=tenant.id,
        is_current=True,
        verification_status='verified'
    ).count()
    
    # Active Alerts for Tenant
    tenant_alerts = Alert.query.filter_by(
        tenant_id=tenant.id,
        status=AlertStatus.NEW
    ).order_by(Alert.severity.desc()).limit(5).all()
    
    # Temperature Compliance Rate
    temp_logs = TemperatureLog.query.join(Shipment).filter(
        Shipment.tenant_id == tenant.id,
        TemperatureLog.timestamp >= datetime.utcnow() - timedelta(days=30)
    ).all()
    
    compliant_readings = sum(1 for log in temp_logs if log.is_within_range)
    temp_compliance_rate = (compliant_readings / len(temp_logs) * 100) if temp_logs else 100
    
    # Upcoming Deliveries (next 24 hours)
    upcoming = Shipment.query.filter(
        Shipment.tenant_id == tenant.id,
        Shipment.status == ShipmentStatus.IN_TRANSIT,
        Shipment.estimated_arrival <= datetime.utcnow() + timedelta(hours=24)
    ).all()
    
    return render_template('dashboard/tenant.html',
                         tenant=tenant,
                         active_shipments=active_shipments,
                         pending_orders=pending_orders,
                         recent_shipments=recent_shipments,
                         total_documents=total_documents,
                         valid_documents=valid_documents,
                         tenant_alerts=tenant_alerts,
                         temp_compliance_rate=round(temp_compliance_rate, 1),
                         upcoming_deliveries=upcoming)


@dashboard_bp.route('/tenant-management')
@login_required
def tenant_management():
    """Tenant Management - Admin only"""
    if not (current_user.is_super_admin or current_user.is_operations_admin):
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.tenant'))
    
    tenants = Tenant.query.all()
    return render_template('dashboard/tenant_management.html', tenants=tenants)


@dashboard_bp.route('/carrier-network')
@login_required
def carrier_network():
    """Carrier Network - Admin only"""
    if not (current_user.is_super_admin or current_user.is_operations_admin):
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.tenant'))
    
    return render_template('dashboard/carrier_network.html')


@dashboard_bp.route('/risk-control')
@login_required
def risk_control():
    """Risk Control Center - Admin only"""
    if not (current_user.is_super_admin or current_user.is_operations_admin):
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.tenant'))
    
    # Get active alerts
    from models import Alert, AlertStatus
    alerts = Alert.query.filter_by(status=AlertStatus.NEW).order_by(Alert.created_at.desc()).limit(20).all()
    return render_template('dashboard/risk_control.html', alerts=alerts)


@dashboard_bp.route('/analytics')
@login_required
def analytics():
    """Analytics Dashboard"""
    tenant_id = session.get('tenant_id')

    if not tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        flash('Please select a tenant context.', 'info')
        return redirect(url_for('auth.select_tenant'))
    
    # Date range
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Build query filters
    filters = []
    if tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        filters.append(Shipment.tenant_id == tenant_id)
    
    # Shipment Analytics
    shipments = Shipment.query.filter(
        Shipment.created_at >= start_date,
        *filters
    ).all()
    
    # Calculate metrics
    total_shipments = len(shipments)
    on_time = sum(1 for s in shipments if s.status == ShipmentStatus.DELIVERED and 
                  (not s.actual_arrival or s.actual_arrival <= s.estimated_arrival))
    on_time_rate = (on_time / total_shipments * 100) if total_shipments else 100
    
    avg_integrity = sum(s.integrity_score for s in shipments) / total_shipments if total_shipments else 100
    
    # Temperature excursions
    excursions_count = sum(len(s.excursions.all()) for s in shipments)
    
    return render_template('dashboard/analytics.html',
                         total_shipments=total_shipments,
                         on_time_rate=round(on_time_rate, 1),
                         avg_integrity=round(avg_integrity, 1),
                         excursions_count=excursions_count,
                         days=days)


@dashboard_bp.route('/settings')
@login_required
def settings():
    """User Settings Page"""
    return render_template('dashboard/settings.html')
