"""
REST API Routes
"""
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
from models import (
    db, Tenant, TenantStatus, User, Shipment, ShipmentStatus, Order, OrderStatus,
    Supplier, Alert, AlertStatus, AlertSeverity, TemperatureLog,
    ComplianceDocument, AuditLog
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ============= Authentication =============

@api_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


# ============= Tenant API =============

@api_bp.route('/tenants')
@login_required
def get_tenants():
    """Get all tenants (admin only)"""
    if not (current_user.is_super_admin or current_user.is_operations_admin):
        return jsonify({'error': 'Access denied'}), 403
    
    tenants = Tenant.query.filter_by(status=TenantStatus.ACTIVE).all()
    return jsonify([t.to_dict() for t in tenants])


@api_bp.route('/tenants/<int:tenant_id>')
@login_required
def get_tenant(tenant_id):
    """Get tenant details"""
    if not current_user.can_access_tenant(tenant_id):
        return jsonify({'error': 'Access denied'}), 403
    
    tenant = Tenant.query.get_or_404(tenant_id)
    return jsonify(tenant.to_dict())


# ============= Shipment API =============

@api_bp.route('/shipments')
@login_required
def get_shipments():
    """Get shipments"""
    tenant_id = session.get('tenant_id') if hasattr(request, 'session') else None
    
    query = Shipment.query
    if tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        query = query.filter_by(tenant_id=tenant_id)
    
    # Filters
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=ShipmentStatus(status))
    
    limit = request.args.get('limit', 50, type=int)
    shipments = query.order_by(Shipment.created_at.desc()).limit(limit).all()
    
    return jsonify([s.to_dict() for s in shipments])


@api_bp.route('/shipments/<int:shipment_id>')
@login_required
def get_shipment(shipment_id):
    """Get shipment details"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if not current_user.can_access_tenant(shipment.tenant_id):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(shipment.to_dict())


@api_bp.route('/shipments/<int:shipment_id>/temperature')
@login_required
def get_shipment_temperature(shipment_id):
    """Get shipment temperature history"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if not current_user.can_access_tenant(shipment.tenant_id):
        return jsonify({'error': 'Access denied'}), 403
    
    logs = shipment.temperature_logs.order_by(TemperatureLog.timestamp.desc()).limit(500).all()
    
    return jsonify({
        'shipment_id': shipment_id,
        'temp_min': shipment.temp_min,
        'temp_max': shipment.temp_max,
        'readings': [log.to_dict() for log in logs]
    })


@api_bp.route('/shipments/<int:shipment_id>/location')
@login_required
def get_shipment_location(shipment_id):
    """Get shipment current location"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if not current_user.can_access_tenant(shipment.tenant_id):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'shipment_id': shipment_id,
        'current_location': shipment.current_location,
        'coordinates': shipment.current_coordinates,
        'progress_percentage': shipment.progress_percentage,
        'status': shipment.status.value
    })


# ============= Order API =============

@api_bp.route('/orders')
@login_required
def get_orders():
    """Get orders"""
    tenant_id = session.get('tenant_id') if hasattr(request, 'session') else None
    
    query = Order.query
    if tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        query = query.filter_by(tenant_id=tenant_id)
    
    orders = query.order_by(Order.created_at.desc()).limit(50).all()
    return jsonify([o.to_dict() for o in orders])


@api_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """Create new order"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Generate order number
    order_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{Order.query.count() + 1:04d}"
    
    order = Order(
        order_number=order_number,
        tenant_id=session.get('tenant_id', current_user.tenant_id),
        status=OrderStatus.DRAFT,
        priority=data.get('priority', 'standard'),
        temperature_zone=data.get('temperature_zone'),
        required_certifications=data.get('required_certifications', []),
        created_by=current_user.id
    )
    
    db.session.add(order)
    db.session.commit()
    
    return jsonify(order.to_dict()), 201


# ============= Supplier API =============

@api_bp.route('/suppliers')
@login_required
def get_suppliers():
    """Get suppliers"""
    suppliers = Supplier.query.filter_by(is_active=True).limit(100).all()
    return jsonify([s.to_dict() for s in suppliers])


@api_bp.route('/suppliers/search')
@login_required
def search_suppliers():
    """Search suppliers with filters"""
    query_str = request.args.get('q', '')
    country = request.args.get('country')
    certifications = request.args.getlist('certifications')
    
    suppliers = Supplier.query.filter_by(is_active=True)
    
    if query_str:
        suppliers = suppliers.filter(Supplier.name.ilike(f'%{query_str}%'))
    
    if country:
        suppliers = suppliers.filter_by(country=country)
    
    results = []
    for supplier in suppliers.all():
        match = supplier.calculate_match_score({
            'certifications': certifications
        })
        results.append({
            'id': supplier.id,
            'name': supplier.name,
            'country': supplier.country,
            'certifications': supplier.certifications,
            'rating': supplier.rating,
            'match_score': match
        })
    
    # Sort by match score
    results.sort(key=lambda x: x['match_score']['percentage'], reverse=True)
    
    return jsonify(results)


# ============= Alert API =============

@api_bp.route('/alerts')
@login_required
def get_alerts():
    """Get alerts"""
    tenant_id = session.get('tenant_id') if hasattr(request, 'session') else None
    
    query = Alert.query
    if tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        query = query.filter_by(tenant_id=tenant_id)
    
    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=AlertStatus(status))
    
    alerts = query.order_by(Alert.created_at.desc()).limit(50).all()
    return jsonify([a.to_dict() for a in alerts])


@api_bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
def acknowledge_alert(alert_id):
    """Acknowledge alert"""
    alert = Alert.query.get_or_404(alert_id)
    
    if not current_user.can_access_tenant(alert.tenant_id):
        return jsonify({'error': 'Access denied'}), 403
    
    alert.acknowledge(current_user.id)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Alert acknowledged'})


@api_bp.route('/alerts/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """Resolve alert"""
    alert = Alert.query.get_or_404(alert_id)
    
    if not current_user.can_access_tenant(alert.tenant_id):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json() or {}
    notes = data.get('notes', '')
    
    alert.resolve(current_user.id, notes)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Alert resolved'})


# ============= Compliance API =============

@api_bp.route('/compliance/documents')
@login_required
def get_compliance_documents():
    """Get compliance documents"""
    tenant_id = session.get('tenant_id') if hasattr(request, 'session') else None
    
    query = ComplianceDocument.query
    if tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        query = query.filter_by(tenant_id=tenant_id)
    
    documents = query.order_by(ComplianceDocument.created_at.desc()).limit(100).all()
    return jsonify([d.to_dict() for d in documents])


@api_bp.route('/compliance/audit-summary')
@login_required
def get_audit_summary():
    """Get audit readiness summary"""
    tenant_id = session.get('tenant_id') if hasattr(request, 'session') else None
    
    query = ComplianceDocument.query
    if tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        query = query.filter_by(tenant_id=tenant_id)
    
    documents = query.all()
    
    total = len(documents)
    valid = sum(1 for d in documents if d.is_valid)
    expired = sum(1 for d in documents if d.is_expired)
    
    return jsonify({
        'total_documents': total,
        'valid_documents': valid,
        'expired_documents': expired,
        'readiness_score': round((valid / total * 100) if total > 0 else 100, 1)
    })


# ============= Dashboard API =============

@api_bp.route('/dashboard/stats')
@login_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    tenant_id = session.get('tenant_id') if hasattr(request, 'session') else None
    
    # Build shipment query
    shipment_query = Shipment.query
    if tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        shipment_query = shipment_query.filter_by(tenant_id=tenant_id)
    
    # Build order query
    order_query = Order.query
    if tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        order_query = order_query.filter_by(tenant_id=tenant_id)
    
    # Build alert query
    alert_query = Alert.query
    if tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        alert_query = alert_query.filter_by(tenant_id=tenant_id)
    
    stats = {
        'total_shipments': shipment_query.count(),
        'active_shipments': shipment_query.filter_by(status=ShipmentStatus.IN_TRANSIT).count(),
        'total_orders': order_query.count(),
        'pending_orders': order_query.filter_by(status=OrderStatus.PENDING_APPROVAL).count(),
        'active_alerts': alert_query.filter(Alert.status.in_([AlertStatus.NEW, AlertStatus.ACKNOWLEDGED])).count(),
        'critical_alerts': alert_query.filter_by(severity=AlertSeverity.CRITICAL, status=AlertStatus.NEW).count()
    }
    
    return jsonify(stats)


# Import session for API
from flask import session
