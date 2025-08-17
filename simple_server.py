#!/usr/bin/env python3
"""
Simple HTTP Server with routing for Legal Platform
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import webbrowser
from urllib.parse import urlparse

class LegalPlatformHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Define route mappings
        routes = {
            '/dashboard': '/dashboard.html',
            '/login': '/login.html',
            '/research': '/research.html',
            '/documents': '/documents.html',
            '/billing': '/billing.html',
            '/clients': '/clients.html',
            '/calendar': '/calendar.html',
            '/analytics': '/analytics.html',
            '/settings': '/settings.html'
        }
        
        # Check if this is a route we need to redirect
        if path in routes:
            print(f"Redirecting {path} to {routes[path]}")
            self.path = routes[path]
        
        # Handle favicon requests
        if path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            self.wfile.write(b'')
            return
        
        # Call the parent method to serve the file
        return SimpleHTTPRequestHandler.do_GET(self)

def run_server():
    # Change to the directory containing the HTML files
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Set up the server
    PORT = 8080
    server = HTTPServer(('localhost', PORT), LegalPlatformHandler)
    
    print(f"🚀 Legal Platform Server Started!")
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
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        server.shutdown()

if __name__ == "__main__":
    run_server() 