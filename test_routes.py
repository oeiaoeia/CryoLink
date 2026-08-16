import os
import sys
from app import create_app, db
from models import User, Tenant, TenantStatus, UserStatus

def test_all_routes():
    # Set test environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'
    
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            # Find the admin user
            admin = User.query.filter_by(email='mysha@cryolink.com').first()
            if not admin:
                from init_db import init_db, seed_data
                init_db()
                seed_data()
                admin = User.query.filter_by(email='mysha@cryolink.com').first()
            
            # Login
            response = client.post('/auth/login', data={
                'email': 'mysha@cryolink.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            if b'Invalid email or password' in response.data:
                print("Login failed!")
                return
            else:
                print("✓ Logged in as mysha@cryolink.com")
            
            # Get all routes
            rules = []
            for rule in app.url_map.iter_rules():
                if 'GET' in rule.methods and '<' not in str(rule):
                    rules.append(str(rule))
            
            # Also add some parameterized routes manually based on existing data
            from models import Order, Shipment, ComplianceDocument, Supplier
            
            order = Order.query.first()
            if order:
                rules.extend([f'/orders/{order.id}', f'/orders/{order.id}/approve'])
                
            shipment = Shipment.query.first()
            if shipment:
                rules.extend([
                    f'/shipments/{shipment.id}', 
                    f'/shipments/{shipment.id}/track',
                    f'/shipments/{shipment.id}/temperature',
                    f'/shipments/{shipment.id}/incidents',
                    f'/shipments/{shipment.id}/edit'
                ])
                
            doc = ComplianceDocument.query.first()
            if doc:
                rules.append(f'/compliance/{doc.id}')
                
            supplier = Supplier.query.first()
            if supplier:
                rules.append(f'/orders/suppliers/{supplier.id}')

            print(f"Testing {len(rules)} routes...")
            
            failed = []
            passed = 0
            
            for route in set(rules):
                try:
                    res = client.get(route)
                    if res.status_code in [200, 302, 304]:
                        passed += 1
                        print(f"✓ GET {route} -> {res.status_code}")
                    else:
                        failed.append((route, res.status_code))
                        print(f"✗ GET {route} -> {res.status_code}")
                except Exception as e:
                    failed.append((route, str(e)))
                    print(f"✗ GET {route} -> {str(e)}")
            
            print("\n" + "="*40)
            print(f"RESULTS: {passed} passed, {len(failed)} failed")
            if failed:
                print("FAILED ROUTES:")
                for route, status in failed:
                    print(f"  - {route}: {status}")
            else:
                print("All routes OK!")

if __name__ == '__main__':
    test_all_routes()
