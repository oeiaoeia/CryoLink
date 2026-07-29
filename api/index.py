"""
Vercel Serverless Entry Point for CryoLink
Exposes the Flask WSGI app for Vercel's Python runtime.
"""
import sys
import os

# Add parent directory to path so imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Create the Flask application — Vercel's @vercel/python runtime
# automatically handles WSGI apps exposed as a module-level `app` variable.
from app import create_app

app = create_app('production')
