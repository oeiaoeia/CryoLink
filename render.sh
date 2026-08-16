#!/bin/bash
# Render.com Build Script
set -e

echo "🚀 Building CryoLink for Render.com..."

# Install dependencies
pip install -r requirements.txt

# Initialize and seed database schema
python init_db.py

echo "✅ Render build complete!"

