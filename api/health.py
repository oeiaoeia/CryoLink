"""
Vercel Health Check Endpoint
Simple serverless function to test deployment.
"""
from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def health(path):
    """Simple health check handler"""
    return jsonify({
        "status": "healthy",
        "service": "CryoLink"
    })
