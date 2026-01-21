"""
Main entry point for the Face Recognition Flask application.
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.routes import app

if __name__ == '__main__':
    import os
    print("=" * 60)
    print("🔍 Face Recognition System")
    print("=" * 60)
    print("Starting Flask application...")
    port = int(os.environ.get('PORT', 5000))
    print(f"Open your browser and go to: http://localhost:{port}")
    print("=" * 60)
    app.run(debug=False, port=port, host='0.0.0.0')
