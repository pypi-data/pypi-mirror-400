
from flask import Flask, render_template_string, send_from_directory
import sys
import os
import subprocess
import argparse
import threading
import time
import socket
import tempfile
import shutil


keep_alive_time = 0
shutdown_event = threading.Event()


def find_browser(browser_name):
    browser_paths = {
        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "firefox": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ],
        "edge": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ],
    }

    for path in browser_paths.get(browser_name.lower(), []):
        if os.path.isfile(path):
            return path
    return None


def auto_detect_browser():
    for browser in ["chrome", "firefox", "edge"]:
        path = find_browser(browser)
        if path:
            return path, browser
    return None, None


def open_browser(url, browser_path):
    subprocess.Popen([browser_path, url])


def wait_for_server(host, port, timeout=10):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.1)
        if time.time() - start_time > timeout:
            print("Error: Flask server did not start within the timeout period.")
            sys.exit(1)


def serve_with_flask(html_file, variables, browser_path):
    app = Flask(__name__)
    html_dir = os.path.dirname(os.path.abspath(html_file))

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    ping_script = """
    <script>
        let pingInterval = setInterval(() => {
            navigator.sendBeacon('/ping');
        }, 2000);

        window.addEventListener('beforeunload', () => {
            navigator.sendBeacon('/disconnect');
        });
    </script>
    """

    html_content = html_content.replace("</body>", f"{ping_script}</body>")

    @app.route("/")
    def index():
        return render_template_string(html_content, **variables)

    @app.route("/<path:filename>")
    def serve_static(filename):
        return send_from_directory(html_dir, filename)

    @app.route("/ping", methods=["POST"])
    def ping():
        global keep_alive_time
        keep_alive_time = time.time()
        return "", 204

    @app.route("/disconnect", methods=["POST"])
    def disconnect():
        shutdown_event.set()
        return "", 204

    def monitor():
        """Monitor pings and shut down if the browser tab is closed."""
        global keep_alive_time
        keep_alive_time = time.time()
        timeout_seconds = 5

        while not shutdown_event.is_set():
            if time.time() - keep_alive_time > timeout_seconds:
                print("No ping received. Shutting down server...")
                shutdown_event.set()
                break
            time.sleep(1)

    def run_flask():
        app.run(host="127.0.0.1", port=5000, threaded=True, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    wait_for_server("127.0.0.1", 5000)

    open_browser("http://127.0.0.1:5000", browser_path)

    monitor()

    print("Server shutting down...")

def open_as_html(original_path, browser_path):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_html = os.path.join(tmp, "index.html")
        shutil.copyfile(original_path, tmp_html)
        file_url = f"file:///{tmp_html.replace(os.sep, '/')}"
        open_browser(file_url, browser_path)
        time.sleep(1)

def main():
    parser = argparse.ArgumentParser(
        description="Open an HTML file in a web browser or serve it via Flask."
    )
    parser.add_argument("html_file", help="Path to the HTML file to open.")
    parser.add_argument(
        "-b",
        "--browser",
        help="Browser to use (chrome, firefox, edge). If omitted, auto-detects.",
    )
    parser.add_argument(
        "--flask",
        action="store_true",
        help="Serve the HTML file via Flask instead of opening locally.",
    )
    parser.add_argument(
        "-v",
        "--vars",
        nargs="*",
        help="Optional variables for Flask templates in key=value format.",
    )

    args = parser.parse_args()

    html_file = args.html_file

    if not os.path.isfile(html_file):
        print(f"Error: File '{html_file}' does not exist.")
        sys.exit(1)

    if args.browser:
        browser_path = find_browser(args.browser)
        if not browser_path:
            print(f"Error: Could not find the browser '{args.browser}'.")
            sys.exit(1)
        browser_name = args.browser
    else:
        browser_path, browser_name = auto_detect_browser()
        if not browser_path:
            print("Error: No supported browsers found (Chrome, Firefox, Edge).")
            sys.exit(1)

    if args.flask:
        variables = {}
        if args.vars:
            for var in args.vars:
                if "=" in var:
                    key, value = var.split("=", 1)
                    variables[key] = value
                else:
                    print(
                        f"Warning: Skipping invalid variable format '{var}' (should be key=value)"
                    )

        print(
            f"Serving {html_file} via Flask and opening in {browser_name.capitalize()}..."
        )
        serve_with_flask(html_file, variables, browser_path)

    else:
        abs_path = os.path.abspath(html_file)
        file_url = f"file:///{abs_path.replace(os.sep, '/')}"
        print(f"Opening {html_file} in {browser_name.capitalize()}...")
        ext = os.path.splitext(html_file)[1].lower()
        if ext not in [".html", ".htm"]:
            open_as_html(file_url, browser_path)
        else:
            open_browser(file_url, browser_path)
