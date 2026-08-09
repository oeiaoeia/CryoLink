"""
Shipment Management Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import (
    db, Shipment, ShipmentStatus, Route, RouteLeg, TransportMode,
    TemperatureLog, TemperatureExcursion, Alert, AlertType, AlertSeverity,
    ComplianceDocument, DocumentType
)
from sqlalchemy import desc

shipments_bp = Blueprint('shipments', __name__, url_prefix='/shipments')


@shipments_bp.route('/')
@login_required
def index():
    """List all shipments for tenant"""
    tenant_id = session.get('tenant_id')
    
    # Filter by tenant unless admin
    if current_user.is_super_admin or current_user.is_operations_admin:
        shipments = Shipment.query.order_by(desc(Shipment.created_at)).all()
    else:
        if not tenant_id:
            flash('Please select a tenant context.', 'info')
            return redirect(url_for('auth.select_tenant'))
        shipments = Shipment.query.filter_by(tenant_id=tenant_id).order_by(
            desc(Shipment.created_at)
        ).all()
    
    # Filter by status
    status_filter = request.args.get('status')
    if status_filter:
        shipments = [s for s in shipments if s.status.value == status_filter]
    
    return render_template('shipments/index.html', shipments=shipments)


@shipments_bp.route('/<int:shipment_id>')
@login_required
def detail(shipment_id):
    """Shipment detail view"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    # Check access
    if not current_user.can_access_tenant(shipment.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('shipments.index'))
    
    # Get temperature history (last 100 readings)
    temp_history = shipment.temperature_logs.order_by(
        desc(TemperatureLog.timestamp)
    ).limit(100).all()
    
    # Get excursions
    excursions = shipment.excursions.order_by(desc(TemperatureExcursion.created_at)).all()
    
    # Get alerts
    alerts = shipment.alerts.order_by(desc(Alert.created_at)).limit(10).all()
    
    # Get documents
    documents = shipment.documents.order_by(desc(ComplianceDocument.created_at)).all()
    
    # Get route legs
    route_legs = []
    if shipment.route:
        route_legs = shipment.route.legs.order_by(RouteLeg.sequence).all()
    
    # Calculate statistics
    total_readings = shipment.temperature_logs.count()
    compliant_readings = sum(1 for log in temp_history if log.is_within_range)
    compliance_rate = (compliant_readings / len(temp_history) * 100) if temp_history else 100
    
    return render_template('shipments/detail.html',
                         shipment=shipment,
                         temp_history=temp_history,
                         excursions=excursions,
                         alerts=alerts,
                         documents=documents,
                         route_legs=route_legs,
                         compliance_rate=round(compliance_rate, 1))


@shipments_bp.route('/<int:shipment_id>/track')
@login_required
def track(shipment_id):
    """Live tracking view"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if not current_user.can_access_tenant(shipment.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('shipments.index'))

    # Get current temperature
    current_temp = shipment.get_current_temperature()

    # Get latest coordinates
    latest_log = shipment.temperature_logs.order_by(
        desc(TemperatureLog.timestamp)
    ).first()

    coordinates = latest_log.coordinates if latest_log else shipment.current_coordinates
    
    # Get temperature history (last 24 readings)
    temp_history = shipment.temperature_logs.order_by(
        desc(TemperatureLog.timestamp)
    ).limit(24).all()
    
    # Calculate compliance rate
    total_readings = len(temp_history)
    compliant_readings = sum(1 for log in temp_history if log.is_within_range)
    compliance_rate = (compliant_readings / total_readings * 100) if total_readings > 0 else 100

    return render_template('shipments/track.html',
                         shipment=shipment,
                         current_temp=current_temp,
                         coordinates=coordinates,
                         temp_history=temp_history,
                         compliance_rate=compliance_rate)


@shipments_bp.route('/<int:shipment_id>/temperature')
@login_required
def temperature_log(shipment_id):
    """Temperature log view"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if not current_user.can_access_tenant(shipment.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('shipments.index'))
    
    # Get all temperature logs
    logs = shipment.temperature_logs.order_by(desc(TemperatureLog.timestamp)).all()
    
    # Get excursions
    excursions = shipment.excursions.order_by(desc(TemperatureExcursion.created_at)).all()
    
    return render_template('shipments/temperature.html',
                         shipment=shipment,
                         logs=logs,
                         excursions=excursions)


@shipments_bp.route('/<int:shipment_id>/incidents')
@login_required
def incidents(shipment_id):
    """Incident replay view"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if not current_user.can_access_tenant(shipment.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('shipments.index'))
    
    # Get all incidents/excursions
    excursions = shipment.excursions.order_by(TemperatureExcursion.started_at).all()
    
    # Get timeline events (temperature logs with significant changes)
    logs = shipment.temperature_logs.order_by(TemperatureLog.timestamp).all()
    
    return render_template('shipments/incidents.html',
                         shipment=shipment,
                         excursions=excursions,
                         logs=logs)


@shipments_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new shipment"""
    if request.method == 'POST':
        # Get form data
        product_name = request.form.get('product_name')
        quantity = request.form.get('quantity', type=int)
        unit = request.form.get('unit')
        temp_zone = request.form.get('temp_zone')
        temp_min = request.form.get('temp_min', type=float)
        temp_max = request.form.get('temp_max', type=float)
        
        origin_city = request.form.get('origin_city')
        origin_country = request.form.get('origin_country')
        destination_city = request.form.get('destination_city')
        destination_country = request.form.get('destination_country')
        
        # Generate shipment number
        shipment_number = f"S-{datetime.utcnow().strftime('%Y%m%d')}-{Shipment.query.count() + 1:04d}"
        
        # Create shipment
        shipment = Shipment(
            shipment_number=shipment_number,
            tenant_id=session.get('tenant_id', current_user.tenant_id),
            product_name=product_name,
            quantity=quantity,
            unit=unit,
            temp_zone=temp_zone,
            temp_min=temp_min,
            temp_max=temp_max,
            origin_city=origin_city,
            origin_country=origin_country,
            destination_city=destination_city,
            destination_country=destination_country,
            status=ShipmentStatus.DRAFT,
            created_by=current_user.id
        )
        
        try:
            db.session.add(shipment)
            db.session.commit()
            flash(f'Shipment {shipment_number} created successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to create shipment. Please try again.', 'error')
            return redirect(url_for('shipments.create'))
        
        return redirect(url_for('shipments.detail', shipment_id=shipment.id))
    
    return render_template('shipments/create.html')


@shipments_bp.route('/<int:shipment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(shipment_id):
    """Edit shipment"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if not current_user.can_access_tenant(shipment.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('shipments.index'))
    
    if request.method == 'POST':
        shipment.product_name = request.form.get('product_name')
        shipment.quantity = request.form.get('quantity', type=int)
        shipment.unit = request.form.get('unit')
        shipment.temp_min = request.form.get('temp_min', type=float)
        shipment.temp_max = request.form.get('temp_max', type=float)
        shipment.priority = request.form.get('priority')
        shipment.carrier_name = request.form.get('carrier_name')
        shipment.tracking_number = request.form.get('tracking_number')
        
        try:
            db.session.commit()
            flash('Shipment updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to update shipment.', 'error')
            
        return redirect(url_for('shipments.detail', shipment_id=shipment.id))
    
    return render_template('shipments/edit.html', shipment=shipment)


@shipments_bp.route('/<int:shipment_id>/start')
@login_required
def start_shipment(shipment_id):
    """Start shipment (change status to in_transit)"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if not current_user.can_access_tenant(shipment.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('shipments.index'))
    
    shipment.status = ShipmentStatus.IN_TRANSIT
    shipment.actual_departure = datetime.utcnow()
    
    # Create audit log
    from models import AuditLog
    audit = AuditLog(
        event_type='shipment_started',
        event_category='shipment',
        action='START',
        description=f'Shipment {shipment.shipment_number} started',
        entity_type='Shipment',
        entity_id=shipment.id,
        entity_reference=shipment.shipment_number,
        tenant_id=shipment.tenant_id,
        user_id=current_user.id,
        user_email=current_user.email
    )
    db.session.add(audit)
    try:
        db.session.commit()
        flash('Shipment started successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to start shipment.', 'error')
        
    return redirect(url_for('shipments.track', shipment_id=shipment.id))


@shipments_bp.route('/<int:shipment_id>/complete')
@login_required
def complete_shipment(shipment_id):
    """Complete shipment (change status to delivered)"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if not current_user.can_access_tenant(shipment.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('shipments.index'))
    
    shipment.status = ShipmentStatus.DELIVERED
    shipment.actual_arrival = datetime.utcnow()
    shipment.progress_percentage = 100
    
    try:
        db.session.commit()
        flash('Shipment completed successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to complete shipment.', 'error')
        
    return redirect(url_for('shipments.detail', shipment_id=shipment.id))


@shipments_bp.route('/api/temperature-data/<int:shipment_id>')
@login_required
def api_temperature_data(shipment_id):
    """API endpoint for temperature chart"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if not current_user.can_access_tenant(shipment.tenant_id):
        return jsonify({'error': 'Access denied'}), 403
    
    logs = shipment.temperature_logs.order_by(TemperatureLog.timestamp).all()
    
    data = {
        'labels': [log.timestamp.strftime('%Y-%m-%d %H:%M') for log in logs],
        'temperatures': [log.temperature for log in logs],
        'min_threshold': shipment.temp_min,
        'max_threshold': shipment.temp_max
    }
    
    return jsonify(data)
