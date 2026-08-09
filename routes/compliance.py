"""
Compliance Vault Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_file, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import (
    db, ComplianceDocument, DocumentType, AuditLog, Shipment, Tenant
)
from sqlalchemy import desc
import io
import csv

compliance_bp = Blueprint('compliance', __name__, url_prefix='/compliance')


@compliance_bp.route('/')
@login_required
def index():
    """Compliance Vault - Document Library"""
    tenant_id = session.get('tenant_id')
    
    if not tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        flash('Please select a tenant context.', 'info')
        return redirect(url_for('auth.select_tenant'))
    
    # Filter by tenant
    if current_user.is_super_admin or current_user.is_operations_admin:
        documents = ComplianceDocument.query.order_by(desc(ComplianceDocument.created_at)).all()
    else:
        documents = ComplianceDocument.query.filter_by(tenant_id=tenant_id).order_by(
            desc(ComplianceDocument.created_at)
        ).all()
    
    # Filter by type
    doc_type = request.args.get('type')
    if doc_type:
        documents = [d for d in documents if d.document_type.value == doc_type]
    
    # Filter by status
    status = request.args.get('status')
    if status == 'valid':
        documents = [d for d in documents if d.is_valid]
    elif status == 'expired':
        documents = [d for d in documents if d.is_expired]
    elif status == 'pending':
        documents = [d for d in documents if d.verification_status == 'pending']
    
    # Statistics
    total_docs = len(documents)
    valid_docs = sum(1 for d in documents if d.is_valid)
    expired_docs = sum(1 for d in documents if d.is_expired)
    pending_docs = sum(1 for d in documents if d.verification_status == 'pending')
    
    return render_template('compliance/index.html',
                         documents=documents,
                         total_docs=total_docs,
                         valid_docs=valid_docs,
                         expired_docs=expired_docs,
                         pending_docs=pending_docs)


@compliance_bp.route('/<int:doc_id>')
@login_required
def document_detail(doc_id):
    """Document detail view"""
    document = ComplianceDocument.query.get_or_404(doc_id)
    
    if not current_user.can_access_tenant(document.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('compliance.index'))
    
    # Get related shipment if exists
    shipment = document.shipment if document.shipment_id else None
    
    # Get related supplier if exists
    supplier = document.supplier if document.supplier_id else None
    
    return render_template('compliance/detail.html',
                         document=document,
                         shipment=shipment,
                         supplier=supplier)


@compliance_bp.route('/shipment/<int:shipment_id>')
@login_required
def shipment_documents(shipment_id):
    """Documents for specific shipment"""
    shipment = Shipment.query.get_or_404(shipment_id)
    
    if not current_user.can_access_tenant(shipment.tenant_id):
        flash('Access denied.', 'error')
        return redirect(url_for('compliance.index'))
    
    documents = ComplianceDocument.query.filter_by(shipment_id=shipment_id).order_by(
        desc(ComplianceDocument.created_at)
    ).all()
    
    return render_template('compliance/shipment_docs.html',
                         shipment=shipment,
                         documents=documents)


@compliance_bp.route('/export', methods=['GET', 'POST'])
@login_required
def export():
    """Export compliance documents for audit"""
    tenant_id = session.get('tenant_id')
    
    if not tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        flash('Please select a tenant context.', 'info')
        return redirect(url_for('auth.select_tenant'))
    
    if request.method == 'POST':
        # Get date range
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        include_raw = request.form.get('include_raw') == 'on'
        
        # Build query
        query = ComplianceDocument.query
        
        if not (current_user.is_super_admin or current_user.is_operations_admin):
            query = query.filter_by(tenant_id=tenant_id)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(ComplianceDocument.created_at >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(ComplianceDocument.created_at < end)
        
        documents = query.all()
        
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Document Number', 'Type', 'Title', 'Issued By', 'Issued Date',
            'Valid Until', 'Status', 'Verification', 'Shipment', 'Blockchain Hash'
        ])
        
        # Data
        for doc in documents:
            writer.writerow([
                doc.document_number,
                doc.document_type.value,
                doc.title,
                doc.issued_by,
                doc.issued_date.strftime('%Y-%m-%d') if doc.issued_date else '',
                doc.valid_until.strftime('%Y-%m-%d') if doc.valid_until else '',
                'Valid' if doc.is_valid else 'Expired' if doc.is_expired else 'Pending',
                doc.verification_status,
                doc.shipment.shipment_number if doc.shipment else '',
                doc.blockchain_hash or ''
            ])
        
        # Create response
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'compliance_export_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        )
    
    return render_template('compliance/export.html')


@compliance_bp.route('/audit-report')
@login_required
def audit_report():
    """Generate audit readiness report"""
    tenant_id = session.get('tenant_id')
    
    if not tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        flash('Please select a tenant context.', 'info')
        return redirect(url_for('auth.select_tenant'))
    
    # Get all documents for tenant
    query = ComplianceDocument.query
    if not (current_user.is_super_admin or current_user.is_operations_admin):
        query = query.filter_by(tenant_id=tenant_id)
    
    documents = query.all()
    
    # Calculate audit readiness
    total = len(documents)
    valid = sum(1 for d in documents if d.is_valid)
    expired = sum(1 for d in documents if d.is_expired)
    pending = sum(1 for d in documents if d.verification_status == 'pending')
    
    readiness_score = (valid / total * 100) if total > 0 else 0
    
    # Group by type
    by_type = {}
    for doc in documents:
        doc_type = doc.document_type.value
        if doc_type not in by_type:
            by_type[doc_type] = {'total': 0, 'valid': 0}
        by_type[doc_type]['total'] += 1
        if doc.is_valid:
            by_type[doc_type]['valid'] += 1
    
    # Get expiring soon (next 30 days)
    expiring_soon = [
        d for d in documents
        if d.valid_until and
        datetime.utcnow() < d.valid_until <= datetime.utcnow() + timedelta(days=30)
    ]
    
    return render_template('compliance/audit_report.html',
                         total=total,
                         valid=valid,
                         expired=expired,
                         pending=pending,
                         readiness_score=round(readiness_score, 1),
                         by_type=by_type,
                         expiring_soon=expiring_soon)


@compliance_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload compliance document"""
    if request.method == 'POST':
        # Get form data
        doc_type = request.form.get('document_type')
        title = request.form.get('title')
        issued_by = request.form.get('issued_by')
        issued_date = request.form.get('issued_date')
        valid_until = request.form.get('valid_until')
        shipment_id = request.form.get('shipment_id', type=int)
        
        # Generate document number
        doc_number = f"DOC-{datetime.utcnow().strftime('%Y%m%d')}-{ComplianceDocument.query.count() + 1:04d}"
        
        # Parse dates
        issued = datetime.strptime(issued_date, '%Y-%m-%d') if issued_date else None
        valid = datetime.strptime(valid_until, '%Y-%m-%d') if valid_until else None
        
        # Create document
        document = ComplianceDocument(
            document_number=doc_number,
            document_type=DocumentType(doc_type),
            title=title,
            issued_by=issued_by,
            issued_date=issued,
            valid_until=valid,
            tenant_id=session.get('tenant_id', current_user.tenant.id),
            shipment_id=shipment_id if shipment_id else None,
            created_by=current_user.id,
            verification_status='pending'
        )
        
        # Generate blockchain hash
        document.generate_blockchain_hash()
        
        db.session.add(document)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Failed to upload document.', 'error')
            return redirect(url_for('compliance.upload'))
        
        # Create audit log
        audit = AuditLog(
            event_type='document_uploaded',
            event_category='compliance',
            action='UPLOAD',
            description=f'Document {doc_number} uploaded: {title}',
            entity_type='ComplianceDocument',
            entity_id=document.id,
            entity_reference=doc_number,
            tenant_id=document.tenant_id,
            user_id=current_user.id,
            user_email=current_user.email
        )
        db.session.add(audit)
        try:
            db.session.commit()
            flash(f'Document {doc_number} uploaded successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to log document upload.', 'error')
            
        return redirect(url_for('compliance.document_detail', doc_id=document.id))
    
    # Get shipments for dropdown
    tenant_id = session.get('tenant_id')
    shipments = []
    if tenant_id:
        shipments = Shipment.query.filter_by(tenant_id=tenant_id).all()
    
    return render_template('compliance/upload.html', shipments=shipments)


@compliance_bp.route('/api/verify/<int:doc_id>', methods=['POST'])
@login_required
def verify_document(doc_id):
    """Verify document"""
    document = ComplianceDocument.query.get_or_404(doc_id)
    
    if not current_user.can_access_tenant(document.tenant_id):
        return jsonify({'error': 'Access denied'}), 403
    
    action = request.form.get('action')
    
    if action == 'verify':
        document.verification_status = 'verified'
        document.generate_blockchain_hash()
        message = 'Document verified successfully.'
    elif action == 'reject':
        document.verification_status = 'revoked'
        message = 'Document rejected.'
    else:
        return jsonify({'error': 'Invalid action'}), 400
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to verify document'}), 500
    
    return jsonify({'success': True, 'message': message})


@compliance_bp.route('/audit-log')
@login_required
def audit_log():
    """View audit trail"""
    tenant_id = session.get('tenant_id')
    
    if not tenant_id and not (current_user.is_super_admin or current_user.is_operations_admin):
        flash('Please select a tenant context.', 'info')
        return redirect(url_for('auth.select_tenant'))
    
    # Get audit logs
    query = AuditLog.query
    
    if not (current_user.is_super_admin or current_user.is_operations_admin):
        query = query.filter_by(tenant_id=tenant_id)
    
    # Filter by category
    category = request.args.get('category')
    if category:
        query = query.filter_by(event_category=category)
    
    logs = query.order_by(desc(AuditLog.timestamp)).limit(100).all()
    
    return render_template('compliance/audit_log.html', logs=logs)
