import os
from dotenv import load_dotenv
load_dotenv()

from core.logger import (
    log_info, log_error, log_debug, 
    log_request, SESSION_ID, IS_NEW_SESSION
)

if IS_NEW_SESSION:
    log_info(f"Starting Flask server with session ID: {SESSION_ID}")

from flask import Flask, jsonify, request, session
app = Flask(__name__, 
    static_folder="routes",  
    static_url_path="",
    template_folder="routes"
)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback_secret")
debug_mode = os.getenv("DEBUG", "False").lower() == "true"
port = int(os.getenv("PORT", 5000))

log_debug(f"Flask configuration: debug={debug_mode}, port={port}")
log_debug(f"Static folder: {app.static_folder}")
log_debug(f"Template folder: {app.template_folder}")

@app.before_request
def log_before_request():
    if not request.path.startswith(('/static/', '/favicon.ico')):
        log_debug(f"Request received: {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_after_request(response):
    if not request.path.startswith(('/static/', '/favicon.ico')):
        log_request(request.path, request.method, response.status_code)
    return response

from core.router import register_routes
from core.engine import setup

setup(app)
register_routes(app)

@app.errorhandler(404)
def not_found(error):
    log_error(error)
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    log_error(error)
    return jsonify({"error": "Internal Server Error"}), 500

@app.route('/debug/routes')
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "url": str(rule)
        })
    return jsonify(routes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            session['user'] = username
            return jsonify({"success": True, "message": "Logged in"})
    return '''
        <form method="post">
            <input type="text" name="username" placeholder="Username">
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return jsonify({"success": True, "message": "Logged out"})

if __name__ == "__main__":
    log_info(f"Starting Flask server on port {port} (debug={debug_mode})")
    try:
        app.run(host='0.0.0.0', debug=debug_mode, port=port, use_reloader=True)
    except Exception as e:
        log_error(f"Error starting Flask server: {e}")
        raise