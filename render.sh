#!/bin/bash
# Render.com Deployment Script

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py

# Run the app with gunicorn
gunicorn main:app
