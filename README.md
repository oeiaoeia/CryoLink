# ❄️ CryoLink - Cold-Chain Supply & Logistics Control Tower

[![Live Demo](https://img.shields.io/badge/Live_Demo-https%3A%2F%2Fcryolink.onrender.com%2F-00C853?style=for-the-badge&logo=render&logoColor=white)](https://cryolink.onrender.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

> 🌐 **Live Website**: [https://cryolink.onrender.com/](https://cryolink.onrender.com/)

---

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
- **Liquid Glass UI**: Modern specular refractions, fluid optics, and wave hover physics

## Tech Stack

- **Backend**: Python 3.11+, Flask, SQLAlchemy, Gunicorn
- **Frontend**: HTML5, CSS3 (Liquid Glass UI System), JavaScript, Bootstrap 5, Chart.js
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Authentication**: Flask-Login with bcrypt

---

## 🌐 Live Render Deployment

Access the live production application:
👉 **[https://cryolink.onrender.com/](https://cryolink.onrender.com/)**

### Default Credentials (Live Site & Development)

#### Operations Admin (Internal)
- **Email**: `mysha@cryolink.com`
- **Password**: `password123`

#### Tenant Users
- **PharmaCo**: `raj@pharma.co` / `password123`
- **BioTech**: `sarah@biotech.io` / `password123`
- **VaxCorp**: `admin@vaxcorp.com` / `password123`

---

## Local Installation

### 1. Clone and Setup

```bash
git clone https://github.com/oeiaoeia/CryoLink.git
cd CryoLink
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

## 🚀 Render.com Configuration

CryoLink is pre-configured for automated continuous deployment on **Render.com**.

- **Live URL**: [https://cryolink.onrender.com/](https://cryolink.onrender.com/)
- **Environment**: `Python 3`
- **Build Command**: `./render.sh`
- **Start Command**: `gunicorn main:app`

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
└── static/                # CSS (Liquid Glass UI), JS, Images
```

## License

MIT License
