import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request, session
app = Flask(__name__, 
    static_folder="routes",  
    static_url_path="",
    template_folder="routes"
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback_secret")
debug_mode = os.getenv("DEBUG", "False").lower() == "true"
port = int(os.getenv("PORT", 5000))

from core.logger import log_error
from core.router import ROUTES_DIR, register_routes
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
    app.run(debug=debug_mode, port=port)