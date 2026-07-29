# CryoLink - Quick Start Guide

## Overview

CryoLink is a comprehensive cold-chain supply chain management platform for pharmaceutical logistics. This Python/Flask application provides:

- **Multitenant Architecture** - Complete data isolation for different organizations
- **Real-time Shipment Tracking** - Temperature monitoring with excursion alerts
- **Smart Route Planning** - AI-powered route comparison with risk scoring
- **Procurement System** - Supplier matching with certification validation
- **Compliance Vault** - One-click audit reports and document management
- **Risk Prediction** - Proactive alerts with suggested actions

## Installation

### 1. Navigate to the Application

```bash
cd /Users/paramshankar777gmail.com/Downloads/App
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Initialize Database (if not already done)

```bash
python init_db.py
```

### 4. Start the Application

```bash
python app.py
```

The server will start at `http://localhost:5000`

## Default Login Credentials

All passwords are: **password123**

### Operations Admin (Internal CryoLink Staff)
- **Email**: mysha@cryolink.com
- **Access**: Global operations dashboard, all tenants

### Tenant Users

**PharmaCo International**
- **Email**: raj@pharma.co
- **Role**: Procurement Manager
- **Access**: PharmaCo tenant data only

**BioTech Innovations**
- **Email**: admin@biotech.io
- **Role**: Supply Chain Director
- **Access**: BioTech tenant data only

**VaxCorp Global**
- **Email**: admin@vaxcorp.com
- **Role**: Operations Manager
- **Access**: VaxCorp tenant data only

## Key Features

### Operations Control Tower (Internal Admin)
- Global shipment map with live tracking
- Multi-tenant overview
- Risk alert management
- Carrier performance monitoring

### Client Dashboard (Tenant Users)
- Active shipment tracking
- Temperature compliance monitoring
- Procurement order management
- Compliance document vault

### Shipment Management
- Create and track cold-chain shipments
- Real-time temperature monitoring
- Route comparison and selection
- Incident replay and analysis

### Procurement System
- Smart supplier matching
- Certification validation
- Order management
- Supplier performance tracking

### Compliance Vault
- Document management with blockchain verification
- Audit readiness reports
- One-click export for audits
- Temperature log history

## API Endpoints

### Authentication
- `GET /auth/login` - Login page
- `POST /auth/login` - Login submission
- `GET /auth/logout` - Logout

### Dashboard
- `GET /` - Redirects to appropriate dashboard
- `GET /dashboard/operations` - Operations control tower
- `GET /dashboard/tenant` - Client dashboard

### Shipments
- `GET /shipments` - List all shipments
- `GET /shipments/{id}` - Shipment details
- `GET /shipments/{id}/track` - Live tracking view
- `GET /shipments/{id}/temperature` - Temperature history

### Orders
- `GET /orders` - List procurement orders
- `GET /orders/create` - Create new order
- `GET /orders/suppliers` - Supplier directory

### Compliance
- `GET /compliance` - Document vault
- `GET /compliance/export` - Export audit report
- `GET /compliance/audit-report` - Audit readiness

### REST API
- `GET /api/shipments` - JSON shipment list
- `GET /api/shipments/{id}` - JSON shipment details
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/alerts` - Alert list

## Project Structure

```
App/
├── app.py                 # Main application
├── config.py              # Configuration
├── init_db.py             # Database initialization
├── requirements.txt       # Python dependencies
├── models/                # Database models
│   ├── tenant.py          # Multitenant organizations
│   ├── user.py            # User authentication
│   ├── shipment.py        # Shipment tracking
│   ├── order.py           # Procurement orders
│   ├── temperature.py     # Temperature monitoring
│   ├── compliance.py      # Document management
│   └── alert.py           # Alert system
├── routes/                # Web routes
│   ├── auth.py            # Authentication
│   ├── dashboard.py       # Dashboard views
│   ├── shipments.py       # Shipment management
│   ├── orders.py          # Order processing
│   ├── compliance.py      # Compliance vault
│   └── api.py             # REST API
├── templates/             # HTML templates
│   ├── base.html          # Base layout
│   ├── auth/              # Login, profile
│   ├── dashboard/         # Operations, tenant
│   ├── shipments/         # Shipment views
│   ├── orders/            # Order views
│   └── compliance/        # Document views
├── static/                # Static assets
│   ├── css/style.css      # Custom styles
│   └── js/app.js          # JavaScript utilities
└── utils/                 # Helper modules
    ├── risk_calculator.py # Risk scoring
    ├── route_optimizer.py # Route planning
    └── temperature_sim.py # Temperature simulation
```

## Technology Stack

- **Backend**: Python 3.x, Flask 3.0
- **Database**: SQLAlchemy ORM with SQLite (PostgreSQL ready)
- **Authentication**: Flask-Login with bcrypt password hashing
- **Frontend**: HTML5, Bootstrap 5, Chart.js
- **Real-time**: Flask-SocketIO (disabled for Python 3.14 compatibility)

## Security Features

- **Multitenant Data Isolation** - Each tenant's data is completely separate
- **Password Hashing** - bcrypt with salt
- **Session Management** - Secure cookies with HTTPOnly flag
- **CSRF Protection** - WTForms CSRF tokens
- **Role-Based Access Control** - Different permissions per user role

## Troubleshooting

### Database Issues
```bash
# Reset database
rm cryolink.db
python init_db.py
```

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Module Import Errors
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

1. **Login** with any of the default credentials
2. **Explore** the Operations Control Tower (admin) or Tenant Dashboard
3. **Create** a new shipment or procurement order
4. **Track** shipments in real-time
5. **Generate** compliance reports

## Support

For questions or issues, refer to the README.md or check the application logs.

---

**Note**: This is a conceptual demonstration application. In production, you would need to:
- Enable HTTPS
- Use PostgreSQL instead of SQLite
- Configure proper email notifications
- Enable WebSocket for real-time updates
- Set up proper logging and monitoring
- Implement rate limiting
- Add comprehensive testing
