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

- **Backend**: Python 3.11+, Flask, SQLAlchemy, Gunicorn
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Authentication**: Flask-Login with bcrypt

## Local Installation

### 1. Clone and Setup

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python init_db.py
```

### 3. Run Application

```bash
python app.py
```

Visit `http://localhost:5001` (or `http://localhost:5000`)

---

## 🚀 Deployment on Render.com

CryoLink is pre-configured for seamless deployment on **Render.com**.

1. Connect your repository to **Render.com**.
2. Create a new **Web Service**.
3. Set the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `./render.sh`
   - **Start Command**: `gunicorn main:app`
4. Set environment variables (optional):
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: `your-random-secret-key`

---

## Default Credentials

### Operations Admin (Internal)
- **Email**: `mysha@cryolink.com`
- **Password**: `password123`

### Tenant Users
- **PharmaCo**: `raj@pharma.co` / `password123`
- **BioTech**: `sarah@biotech.io` / `password123`
- **VaxCorp**: `admin@vaxcorp.com` / `password123`

---

## Project Structure

```
CryoLink/
├── app.py                 # Application factory & setup
├── main.py                # Production entry point (Gunicorn)
├── config.py              # Environment configurations
├── init_db.py             # Database creation & seed data
├── Procfile               # Render/Gunicorn process definition
├── render.sh              # Render build script
├── requirements.txt       # Dependencies
├── models/                # Database models
│   ├── tenant.py
│   ├── user.py
│   ├── shipment.py
│   ├── order.py
│   ├── temperature.py
│   ├── compliance.py
│   └── alert.py
├── routes/                # Blueprint routes
│   ├── auth.py
│   ├── dashboard.py
│   ├── shipments.py
│   ├── orders.py
│   ├── compliance.py
│   └── api.py
├── templates/             # HTML Jinja templates
└── static/                # CSS, JS, Images
```

## License

MIT License
