#!/usr/bin/env python3
"""
Simple HTTP Server for Landing Page
Serves the landing page locally for testing and demonstration.
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler with routing support."""
    
    def do_GET(self):
        """Handle GET requests with custom routing."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Handle routing
        if path == '/dashboard':
            self.path = '/dashboard.html'
        elif path == '/login':
            self.path = '/login.html'
        elif path == '/research':
            self.path = '/research.html'
        elif path == '/documents':
            self.path = '/documents.html'
        elif path == '/billing':
            self.path = '/billing.html'
        elif path == '/clients':
            self.path = '/clients.html'
        elif path == '/calendar':
            self.path = '/calendar.html'
        elif path == '/analytics':
            self.path = '/analytics.html'
        elif path == '/settings':
            self.path = '/settings.html'
        elif path == '/favicon.ico':
            # Return a simple favicon response
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            self.wfile.write(b'')  # Empty favicon
            return
        
        # Call the parent method
        super().do_GET()

def serve_landing_page():
    """Serve the landing page on localhost."""
    
    # Change to the directory containing the HTML file
    os.chdir(Path(__file__).parent)
    
    # Set up the server
    PORT = 8081
    Handler = CustomHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 Landing page server started!")
        print(f"📱 Open your browser and go to: http://localhost:{PORT}")
        print(f"📄 Serving: {os.getcwd()}")
        print(f"🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        print(f"🔗 Available routes:")
        print(f"   - / (landing page)")
        print(f"   - /login or /login.html")
        print(f"   - /dashboard or /dashboard.html")
        print(f"   - /research or /research.html")
        print(f"   - /documents or /documents.html")
        print(f"   - /billing or /billing.html")
        print(f"   - /clients or /clients.html")
        print(f"   - /calendar or /calendar.html")
        print(f"   - /analytics or /analytics.html")
        print(f"   - /settings or /settings.html")
        print("-" * 50)
        
        # Try to open the browser automatically
        try:
            webbrowser.open(f'http://localhost:{PORT}')
            print("🌐 Browser opened automatically!")
        except:
            print("⚠️  Could not open browser automatically. Please open manually.")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            httpd.shutdown()

if __name__ == "__main__":
    serve_landing_page() 