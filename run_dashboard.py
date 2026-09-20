"""
run_dashboard.py — ProcureEdge Procurement Analytics
Opens the dashboard in your default browser with one command.
Usage: python run_dashboard.py
"""
import webbrowser, os, http.server, socketserver, threading, time

PORT = 8050
dashboard_dir = os.path.join(os.path.dirname(__file__), "dashboard")
os.chdir(dashboard_dir)

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

def serve():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

t = threading.Thread(target=serve, daemon=True)
t.start()
time.sleep(0.5)

url = f"http://localhost:{PORT}/index.html"
print(f"\n ProcureEdge Procurement Analytics Dashboard")
print(f" Running at: {url}")
print(f" Press Ctrl+C to stop.\n")
webbrowser.open(url)

try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    print("\n Dashboard stopped.")