"""
WSGI entry point for the Flask application.

This file creates the Flask app instance using the application factory
and makes it available for WSGI servers like Gunicorn or Waitress.

It also allows running the Flask development server directly via
`python wsgi.py`.
"""
import os
from app import create_app

# Create the Flask app instance using the application factory
app = create_app()

if __name__ == "__main__":
    # Run the Flask development server
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000)) 
    # Bind to 0.0.0.0 to make it accessible on the network
    print(f"Starting Flask development server on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
