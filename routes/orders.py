"""
Order Management Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import (
    db, Order, OrderStatus, OrderItem, Supplier, Shipment, ShipmentStatus,
    ComplianceDocument, DocumentType
)
from sqlalchemy import desc

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')


@orders_bp.route('/')
@login_required
def index():
    """List all orders for tenant"""
    tenant_id = session.get('tenant_id')
    
    if not tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        flash('Please select a tenant context.', 'info')
        return redirect(url_for('auth.select_tenant'))
    
    # Filter by tenant
    if current_user.is_super_admin or current_user.is_operations_admin:
        orders = Order.query.order_by(desc(Order.created_at)).all()
    else:
        orders = Order.query.filter_by(tenant_id=tenant_id).order_by(
            desc(Order.created_at)
        ).all()
    
    # Filter by status
    status_filter = request.args.get('status')
    if status_filter:
        orders = [o for o in orders if o.status.value == status_filter]
    
    return render_template('orders/index.html', orders=orders)


@orders_bp.route('/<int:order_id>')
@login_required
def detail(order_id):
    """Order detail view"""
    order = Order.query.get_or_404(order_id)
    
    if not current_user.can_access_tenant(order.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('orders.index'))
    
    # Get order items
    items = order.items.all()
    
    # Get matching suppliers if in supplier_matching status
    match_scores = []
    if order.status == OrderStatus.SUPPLIER_MATCHING:
        match_scores = order.get_match_scores()
    
    return render_template('orders/detail.html',
                         order=order,
                         items=items,
                         match_scores=match_scores)


@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new order"""
    if request.method == 'POST':
        # Get form data
        priority = request.form.get('priority')
        temperature_zone = request.form.get('temperature_zone')
        delivery_deadline = request.form.get('delivery_deadline')
        shipping_address = request.form.get('shipping_address')
        shipping_city = request.form.get('shipping_city')
        shipping_country = request.form.get('shipping_country')
        
        # Required certifications
        required_certs = request.form.getlist('required_certifications')
        
        # Generate order number
        order_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{Order.query.count() + 1:04d}"
        
        # Parse deadline
        deadline = None
        if delivery_deadline and delivery_deadline != 'dd/mm/yyyy':
            try:
                deadline = datetime.strptime(delivery_deadline, '%Y-%m-%d')
            except ValueError:
                deadline = None
        
        # Create order
        order = Order(
            order_number=order_number,
            tenant_id=session.get('tenant_id', current_user.tenant_id),
            status=OrderStatus.DRAFT,
            priority=priority,
            temperature_zone=temperature_zone,
            required_certifications=required_certs,
            delivery_deadline=deadline,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_country=shipping_country,
            created_by=current_user.id
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Add order items from form
        product_names = request.form.getlist('product_name[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')
        
        for i, name in enumerate(product_names):
            if name:
                item = OrderItem(
                    order_id=order.id,
                    product_name=name,
                    quantity=int(quantities[i]) if quantities[i] else 1,
                    unit=units[i] if units[i] else 'units'
                )
                db.session.add(item)
        
        try:
            db.session.commit()
            flash(f'Order {order_number} created successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to create order. Please try again.', 'error')
            return redirect(url_for('orders.create'))

        return redirect(url_for('orders.detail', order_id=order.id))
    
    # Get available suppliers for form
    suppliers = Supplier.query.filter_by(is_active=True).all()
    
    return render_template('orders/create.html', suppliers=suppliers)


@orders_bp.route('/<int:order_id>/select-supplier', methods=['POST'])
@login_required
def select_supplier(order_id):
    """Select supplier for order"""
    order = Order.query.get_or_404(order_id)
    
    if not current_user.can_access_tenant(order.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('orders.index'))
    
    supplier_id = request.form.get('supplier_id', type=int)
    supplier = Supplier.query.get(supplier_id)
    
    if not supplier:
        flash('Invalid supplier selected.', 'error')
        return redirect(url_for('orders.detail', order_id=order.id))
    
    order.selected_supplier = supplier
    order.status = OrderStatus.SUPPLIER_CONFIRMED
    
    try:
        db.session.commit()
        flash(f'Supplier {supplier.name} selected successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to select supplier.', 'error')

    return redirect(url_for('orders.detail', order_id=order.id))


@orders_bp.route('/<int:order_id>/approve')
@login_required
def approve_order(order_id):
    """Approve order"""
    order = Order.query.get_or_404(order_id)
    
    if not current_user.can_access_tenant(order.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('orders.index'))
    
    try:
        if order.status == OrderStatus.DRAFT:
            order.status = OrderStatus.PENDING_APPROVAL
            db.session.commit()
            flash('Order submitted for approval.', 'success')
        elif order.status == OrderStatus.PENDING_APPROVAL:
            order.status = OrderStatus.APPROVED
            db.session.commit()
            flash('Order approved.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating order status.', 'error')
    
    return redirect(url_for('orders.detail', order_id=order.id))


@orders_bp.route('/<int:order_id>/create-shipment')
@login_required
def create_shipment(order_id):
    """Create shipment from order"""
    order = Order.query.get_or_404(order_id)
    
    if not current_user.can_access_tenant(order.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('orders.index'))
    
    if order.status not in [OrderStatus.SUPPLIER_CONFIRMED, OrderStatus.PROCESSING]:
        flash('Order must have supplier confirmed before creating shipment.', 'error')
        return redirect(url_for('orders.detail', order_id=order.id))
    
    # Create shipment
    shipment_number = f"S-{datetime.utcnow().strftime('%Y%m%d')}-{Shipment.query.count() + 1:04d}"
    
    shipment = Shipment(
        shipment_number=shipment_number,
        tenant_id=order.tenant_id,
        product_name=', '.join([item.product_name for item in order.items]),
        quantity=order.total_quantity,
        unit=order.items.first().unit if order.items.first() else 'units',
        temp_zone=order.temperature_zone or 'refrigerated',
        temp_min=2,
        temp_max=8,
        origin_city=order.selected_supplier.city if order.selected_supplier else 'Unknown',
        origin_country=order.selected_supplier.country if order.selected_supplier else 'Unknown',
        destination_city=order.shipping_city or 'Unknown',
        destination_country=order.shipping_country or 'Unknown',
        status=ShipmentStatus.SCHEDULED,
        estimated_arrival=order.delivery_deadline,
        created_by=current_user.id
    )
    
    db.session.add(shipment)
    db.session.flush()
    
    # Link order to shipment
    order.shipment_id = shipment.id
    order.status = OrderStatus.IN_TRANSIT
    
    try:
        db.session.commit()
        flash(f'Shipment {shipment_number} created from order.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to create shipment from order.', 'error')
        return redirect(url_for('orders.detail', order_id=order.id))

    return redirect(url_for('shipments.detail', shipment_id=shipment.id))


@orders_bp.route('/suppliers')
@login_required
def suppliers():
    """List suppliers"""
    suppliers = Supplier.query.filter_by(is_active=True).all()
    return render_template('orders/suppliers.html', suppliers=suppliers)


@orders_bp.route('/suppliers/<int:supplier_id>')
@login_required
def supplier_detail(supplier_id):
    """Supplier detail view"""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # Get supplier documents
    documents = supplier.certification_docs.all() if hasattr(supplier, 'certification_docs') else []
    
    return render_template('orders/supplier_detail.html',
                         supplier=supplier,
                         documents=documents)


@orders_bp.route('/api/suppliers/search')
@login_required
def search_suppliers():
    """API endpoint to search suppliers"""
    query = request.args.get('q', '')
    country = request.args.get('country', '')
    certifications = request.args.getlist('certifications', [])
    
    suppliers = Supplier.query.filter_by(is_active=True)
    
    if query:
        suppliers = suppliers.filter(Supplier.name.ilike(f'%{query}%'))
    
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
            'match_score': match['percentage']
        })
    
    return jsonify(results)
