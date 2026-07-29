"""
Database Initialization Script
Creates tables and seeds initial data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (
    Tenant, TenantStatus, User, UserRole, UserStatus,
    Shipment, ShipmentStatus, Route, RouteLeg, TransportMode,
    Order, OrderStatus, OrderItem, Supplier,
    TemperatureLog, TemperatureExcursion,
    ComplianceDocument, DocumentType, AuditLog,
    Alert, AlertType, AlertStatus, AlertSeverity
)
from datetime import datetime, timedelta
import random


def init_db():
    """Initialize database with tables"""
    with app.app_context():
        db.create_all()
        print("✓ Database tables created")


def seed_data():
    """Seed database with initial data"""
    with app.app_context():
        # Check if already seeded
        if Tenant.query.first():
            print("⚠ Database already has data. Skipping seed.")
            return
        
        print("Seeding database...")
        
        # ============= Create Tenants =============
        tenants = [
            Tenant(
                name='PharmaCo International',
                domain='pharma.co',
                tenant_id='PHARM001',
                email='contact@pharma.co',
                phone='+1-555-0100',
                country='United States',
                status=TenantStatus.ACTIVE,
                primary_color='#0066CC',
                certifications=['GMP', 'FDA', 'ISO_9001']
            ),
            Tenant(
                name='BioTech Innovations',
                domain='biotech.io',
                tenant_id='BIO002',
                email='info@biotech.io',
                phone='+49-30-123456',
                country='Germany',
                status=TenantStatus.ACTIVE,
                primary_color='#00A8E8',
                certifications=['GMP', 'EMA', 'ISO_13485']
            ),
            Tenant(
                name='VaxCorp Global',
                domain='vaxcorp.com',
                tenant_id='VAX003',
                email='operations@vaxcorp.com',
                phone='+41-22-1234567',
                country='Switzerland',
                status=TenantStatus.ACTIVE,
                primary_color='#9C27B0',
                certifications=['GMP', 'FDA', 'EMA', 'GDP']
            )
        ]
        
        for tenant in tenants:
            db.session.add(tenant)
        db.session.flush()
        print(f"✓ Created {len(tenants)} tenants")
        
        # ============= Create Users =============
        users = [
            # Operations Admin (Internal)
            User(
                email='mysha@cryolink.com',
                first_name='Mysha',
                last_name='Admin',
                job_title='CTO / Operations Admin',
                role=UserRole.OPERATIONS_ADMIN,
                status=UserStatus.ACTIVE,
                tenant_id=None
            ),
            # PharmaCo Users
            User(
                email='raj@pharma.co',
                first_name='Dr. Raj',
                last_name='Kumar',
                job_title='Procurement Manager',
                role=UserRole.TENANT_ADMIN,
                status=UserStatus.ACTIVE,
                tenant_id=tenants[0].id
            ),
            User(
                email='sarah@pharma.co',
                first_name='Sarah',
                last_name='Johnson',
                job_title='Logistics Coordinator',
                role=UserRole.LOGISTICS_COORDINATOR,
                status=UserStatus.ACTIVE,
                tenant_id=tenants[0].id
            ),
            # BioTech Users
            User(
                email='admin@biotech.io',
                first_name='Klaus',
                last_name='Mueller',
                job_title='Supply Chain Director',
                role=UserRole.TENANT_ADMIN,
                status=UserStatus.ACTIVE,
                tenant_id=tenants[1].id
            ),
            # VaxCorp Users
            User(
                email='admin@vaxcorp.com',
                first_name='Elena',
                last_name='Schmidt',
                job_title='Operations Manager',
                role=UserRole.TENANT_ADMIN,
                status=UserStatus.ACTIVE,
                tenant_id=tenants[2].id
            )
        ]
        
        for user in users:
            user.set_password('password123')
            db.session.add(user)
        db.session.flush()
        print(f"✓ Created {len(users)} users")
        
        # ============= Create Suppliers =============
        suppliers = [
            Supplier(
                name='ChemGlobal Industries',
                code='SUP001',
                email='sales@chemglobal.com',
                phone='+65-6123-4567',
                address='12 Tuas Avenue',
                city='Singapore',
                country='Singapore',
                postal_code='639284',
                certifications=['GMP', 'FDA', 'ISO_9001'],
                product_categories=['Lipids', 'Buffers', 'Excipients'],
                temperature_zones=['refrigerated', 'frozen'],
                rating=4.9,
                on_time_delivery_rate=97.2,
                quality_score=98.5,
                is_verified=True
            ),
            Supplier(
                name='BioSupply Co',
                code='SUP002',
                email='orders@biosupply.de',
                phone='+49-89-123456',
                address='Industriestraße 45',
                city='Munich',
                country='Germany',
                postal_code='80339',
                certifications=['GMP', 'EMA', 'ISO_13485'],
                product_categories=['Reagents', 'Plasma', 'Cell Culture'],
                temperature_zones=['refrigerated', 'frozen', 'ultra_cold'],
                rating=4.7,
                on_time_delivery_rate=94.5,
                quality_score=96.2,
                is_verified=True
            ),
            Supplier(
                name='PharmaRaw Inc',
                code='SUP003',
                email='sales@pharmaraw.com',
                phone='+1-610-555-0200',
                address='500 Innovation Drive',
                city='Philadelphia',
                country='United States',
                postal_code='19104',
                certifications=['GMP', 'FDA'],
                product_categories=['APIs', 'Excipients', 'Packaging'],
                temperature_zones=['refrigerated'],
                rating=4.8,
                on_time_delivery_rate=95.8,
                quality_score=97.0,
                is_verified=True
            )
        ]
        
        for supplier in suppliers:
            db.session.add(supplier)
        db.session.flush()
        print(f"✓ Created {len(suppliers)} suppliers")
        
        # ============= Create Sample Shipments =============
        shipments_data = [
            {
                'tenant': tenants[0],
                'product': 'mRNA Vaccine Raw Material',
                'temp_zone': 'refrigerated',
                'temp_min': 2,
                'temp_max': 8,
                'origin': ('Singapore', 'Singapore'),
                'destination': ('Boston', 'United States'),
                'status': ShipmentStatus.IN_TRANSIT,
                'progress': 68
            },
            {
                'tenant': tenants[0],
                'product': 'Biologic Reagent',
                'temp_zone': 'frozen',
                'temp_min': -25,
                'temp_max': -15,
                'origin': ('Berlin', 'Germany'),
                'destination': ('Zurich', 'Switzerland'),
                'status': ShipmentStatus.IN_TRANSIT,
                'progress': 92
            },
            {
                'tenant': tenants[1],
                'product': 'Cell Therapy Material',
                'temp_zone': 'ultra_cold',
                'temp_min': -80,
                'temp_max': -60,
                'origin': ('San Francisco', 'United States'),
                'destination': ('Frankfurt', 'Germany'),
                'status': ShipmentStatus.IN_TRANSIT,
                'progress': 45
            },
            {
                'tenant': tenants[2],
                'product': 'Vaccine Adjuvant',
                'temp_zone': 'refrigerated',
                'temp_min': 2,
                'temp_max': 8,
                'origin': ('Mumbai', 'India'),
                'destination': ('Geneva', 'Switzerland'),
                'status': ShipmentStatus.DELAYED,
                'progress': 55
            },
            {
                'tenant': tenants[0],
                'product': 'Monoclonal Antibodies',
                'temp_zone': 'refrigerated',
                'temp_min': 2,
                'temp_max': 8,
                'origin': ('Tokyo', 'Japan'),
                'destination': ('San Francisco', 'United States'),
                'status': ShipmentStatus.DELIVERED,
                'progress': 100
            }
        ]
        
        for i, data in enumerate(shipments_data):
            shipment = Shipment(
                shipment_number=f"S-{datetime.utcnow().strftime('%Y%m%d')}-{i+1:04d}",
                tenant_id=data['tenant'].id,
                product_name=data['product'],
                quantity=random.randint(10, 500),
                unit='units',
                temp_zone=data['temp_zone'],
                temp_min=data['temp_min'],
                temp_max=data['temp_max'],
                origin_city=data['origin'][0],
                origin_country=data['origin'][1],
                destination_city=data['destination'][0],
                destination_country=data['destination'][1],
                status=data['status'],
                progress_percentage=data['progress'],
                risk_score=random.randint(10, 50),
                integrity_score=random.randint(85, 99),
                delay_probability=random.randint(5, 30),
                current_location=f"In transit from {data['origin'][0]}",
                estimated_arrival=datetime.utcnow() + timedelta(hours=random.randint(2, 72)),
                created_by=users[1].id if data['tenant'] == tenants[0] else users[3].id
            )
            db.session.add(shipment)
        db.session.flush()
        print(f"✓ Created {len(shipments_data)} shipments")
        
        # ============= Create Sample Orders =============
        orders_data = [
            {
                'tenant': tenants[0],
                'supplier': suppliers[0],
                'products': ['Lipid SM-102', 'Cholesterol', 'PEG-DMG'],
                'status': OrderStatus.IN_TRANSIT
            },
            {
                'tenant': tenants[1],
                'supplier': suppliers[1],
                'products': ['Cell Culture Media', 'Growth Factors'],
                'status': OrderStatus.PROCESSING
            },
            {
                'tenant': tenants[2],
                'supplier': suppliers[2],
                'products': ['Vaccine Adjuvant AS01', 'Buffer Solution'],
                'status': OrderStatus.SUPPLIER_MATCHING
            }
        ]
        
        for data in orders_data:
            order = Order(
                order_number=f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{data['tenant'].id}",
                tenant_id=data['tenant'].id,
                status=data['status'],
                temperature_zone='refrigerated',
                required_certifications=['GMP', 'FDA'],
                selected_supplier_id=data['supplier'].id,
                created_by=users[1].id
            )
            db.session.add(order)
            db.session.flush()
            
            # Add order items
            for product in data['products']:
                item = OrderItem(
                    order_id=order.id,
                    product_name=product,
                    quantity=random.randint(5, 50),
                    unit='units'
                )
                db.session.add(item)
        
        db.session.flush()
        print(f"✓ Created {len(orders_data)} orders")
        
        # ============= Create Sample Temperature Logs =============
        all_shipments = Shipment.query.all()
        for shipment in all_shipments:
            # Generate temperature readings for past 24-48 hours
            num_readings = random.randint(24, 48)
            base_temp = (shipment.temp_min + shipment.temp_max) / 2
            
            for i in range(num_readings):
                timestamp = datetime.utcnow() - timedelta(hours=num_readings - i)
                
                # Add some variation
                variation = random.uniform(-1.5, 1.5)
                temp = base_temp + variation
                
                # Occasionally add excursion
                if random.random() < 0.05:  # 5% chance
                    temp = shipment.temp_max + random.uniform(1, 4)
                
                log = TemperatureLog(
                    shipment_id=shipment.id,
                    temperature=round(temp, 1),
                    location=shipment.current_location or 'In transit',
                    timestamp=timestamp
                )
                db.session.add(log)
        
        db.session.flush()
        print(f"✓ Created temperature logs")
        
        # ============= Create Sample Alerts =============
        alert_types = [
            (AlertType.TEMPERATURE_EXCURSION, AlertSeverity.HIGH, 'Temperature excursion detected'),
            (AlertType.DELAY_RISK, AlertSeverity.MEDIUM, 'Potential delay predicted'),
            (AlertType.CUSTOMS_ISSUE, AlertSeverity.MEDIUM, 'Customs clearance pending'),
            (AlertType.DOCUMENT_EXPIRING, AlertSeverity.LOW, 'Certificate expiring soon')
        ]
        
        for i, (alert_type, severity, title) in enumerate(alert_types):
            if i < len(all_shipments):
                shipment = all_shipments[i]
                alert = Alert(
                    alert_number=f"ALT-{datetime.utcnow().strftime('%Y%m%d')}-{i+1:04d}",
                    alert_type=alert_type,
                    severity=severity,
                    title=title,
                    message=f'Alert for shipment {shipment.shipment_number}',
                    tenant_id=shipment.tenant_id,
                    shipment_id=shipment.id,
                    status=AlertStatus.NEW if i < 2 else AlertStatus.ACKNOWLEDGED,
                    suggested_actions=['Review shipment details', 'Contact carrier', 'Notify client']
                )
                db.session.add(alert)
        
        db.session.flush()
        print(f"✓ Created alerts")
        
        # ============= Create Sample Compliance Documents =============
        doc_types = [
            DocumentType.CERTIFICATE_OF_ANALYSIS,
            DocumentType.GDP_CERTIFICATE,
            DocumentType.SHIPPING_MANIFEST,
            DocumentType.CHAIN_OF_CUSTODY
        ]
        
        for shipment in all_shipments[:3]:
            for doc_type in doc_types:
                doc = ComplianceDocument(
                    document_number=f"DOC-{shipment.id}-{doc_type.value[:3].upper()}",
                    document_type=doc_type,
                    title=f'{doc_type.value.replace("_", " ").title()} for {shipment.shipment_number}',
                    tenant_id=shipment.tenant_id,
                    shipment_id=shipment.id,
                    issued_by='Quality Assurance Dept',
                    issued_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                    valid_until=datetime.utcnow() + timedelta(days=random.randint(30, 365)),
                    verification_status='verified',
                    is_current=True,
                    created_by=users[1].id
                )
                doc.generate_blockchain_hash()
                db.session.add(doc)
        
        db.session.flush()
        print(f"✓ Created compliance documents")
        
        # Commit all
        db.session.commit()
        
        # Print credentials
        print("\n" + "="*60)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print("="*60)
        print("\nDefault Credentials (all passwords: 'password123'):\n")
        print("Operations Admin:")
        print("  Email: mysha@cryolink.com")
        print("\nTenant Users:")
        print("  PharmaCo:  raj@pharma.co")
        print("  BioTech:   admin@biotech.io")
        print("  VaxCorp:   admin@vaxcorp.com")
        print("\n" + "="*60)


if __name__ == '__main__':
    print("Initializing CryoLink Database...")
    init_db()
    seed_data()
    print("\n✓ Database ready!")
