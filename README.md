# CryoLink - Cold-Chain Supply & Logistics Control Tower

## Overview

CryoLink is an intelligent, web-based multitenant platform designed for pharmaceutical cold-chain logistics. It unifies raw material procurement, multimodal route planning, live temperature monitoring, and compliance management into a single operational control tower.

## Features

- **Multitenant Architecture**: Complete data isolation for different pharmaceutical companies
- **Real-time Temperature Monitoring**: Live tracking with excursion alerts
- **Smart Route Planning**: AI-powered route comparison with risk scoring
- **Procurement System**: Supplier matching with certification validation
- **Compliance Vault**: One-click audit reports and document management
- **Risk Prediction**: Proactive alerts with suggested actions
- **Operations Control Tower**: Global shipment visibility for admins
- **Client Dashboard**: Shipment tracking and compliance for tenants

## Tech Stack

- **Backend**: Python 3.11+, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
- **Database**: PostgreSQL / SQLite
- **Real-time**: Flask-SocketIO
- **Authentication**: Flask-Login with bcrypt

## Installation

### 1. Clone and Setup

```bash
cd App
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///cryolink.db
```

### 3. Initialize Database

```bash
python init_db.py
```

### 4. Run Application

```bash
python app.py
```

Visit `http://localhost:5000`

## Default Credentials

### Operations Admin (Internal)
- **Email**: mysha@cryolink.com
- **Password**: admin123

### Tenant Users
- **PharmaCo**: raj@pharma.co / password123
- **BioTech**: sarah@biotech.io / password123
- **VaxCorp**: admin@vaxcorp.com / password123

## Project Structure

```
App/
├── app.py                 # Main application entry
├── config.py              # Configuration settings
├── init_db.py             # Database initialization
├── models/                # Database models
│   ├── __init__.py
│   ├── tenant.py          # Tenant/Organization model
│   ├── user.py            # User authentication
│   ├── shipment.py        # Shipment tracking
│   ├── order.py           # Procurement orders
│   ├── temperature.py     # Temperature logs
│   ├── compliance.py      # Documents & compliance
│   └── alert.py           # Alerts & notifications
├── routes/                # API routes
│   ├── __init__.py
│   ├── auth.py            # Authentication
│   ├── dashboard.py       # Dashboard views
│   ├── shipments.py       # Shipment management
│   ├── orders.py          # Order processing
│   ├── compliance.py      # Compliance vault
│   └── api.py             # REST API
├── templates/             # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard/
│   ├── shipments/
│   ├── orders/
│   └── compliance/
├── static/                # Static assets
│   ├── css/
│   ├── js/
│   └── images/
└── utils/                 # Helper functions
    ├── risk_calculator.py
    ├── route_optimizer.py
    └── temperature_sim.py
```

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `POST /api/register` - Tenant registration

### Shipments
- `GET /api/shipments` - List shipments
- `GET /api/shipments/<id>` - Shipment details
- `POST /api/shipments` - Create shipment
- `GET /api/shipments/<id>/temperature` - Temperature log

### Orders
- `GET /api/orders` - List orders
- `POST /api/orders` - Create order
- `GET /api/orders/suppliers` - Find suppliers

### Compliance
- `GET /api/compliance/documents` - List documents
- `POST /api/compliance/export` - Export audit report

## License

MIT License - Educational/Conceptual Project
