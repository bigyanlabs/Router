import os
import importlib.util
from flask import Flask, request, jsonify, render_template
from core.middleware import auth_middleware, auth_required
from core.logger import log_request, log_error
from typing import Optional, Any, Dict

ROUTES_DIR: str = "routes"

def register_routes(app: Flask) -> None:
    """Dynamically registers routes based on folder structure."""
    route_functions: Dict[str, Any] = {}  
    
    for root, dirs, files in os.walk(ROUTES_DIR):
        if "controller.py" not in files:
            continue
            
        rel_path: str = root.replace("\\", "/").replace(ROUTES_DIR, "").strip("/")
        route_path: str = f"/{rel_path}" if rel_path else "/"
        
        flask_route: str = route_path
        if "[" in flask_route:
            segments = flask_route.split("/")
            for i, segment in enumerate(segments):
                if segment.startswith("[") and segment.endswith("]"):
                    param_name = segment[1:-1]
                    segments[i] = f"<{param_name}>"
            flask_route = "/".join(segments)
            
        module_name: str = rel_path.replace("/", ".") if rel_path else "index"
        module_path: str = os.path.join(root, "controller.py")
        
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        endpoint_name = f"route_{rel_path.replace('/', '_').replace('[', '').replace(']', '')}"
        if not endpoint_name or endpoint_name == "route_":
            endpoint_name = "route_index"
            
        def create_route_handler(mod, r_path):
            @auth_required
            def handler(*args, **kwargs):
                try:
                    response = mod.handler(request, **kwargs)
                    log_request(r_path, request.method, 200)
                    return response
                except Exception as e:
                    log_error(e)
                    return jsonify({"error": "Internal Server Error"}), 500
            
            handler.__name__ = f"handle_{endpoint_name}"
            return handler
        
        route_functions[flask_route] = (create_route_handler(module, flask_route), endpoint_name)
    
    for flask_route, (handler_func, endpoint) in route_functions.items():
        app.route(flask_route, methods=["GET", "POST"], endpoint=endpoint)(handler_func)
        
    @app.route('/<path:route_path>/<filename>')
    def serve_route_static(route_path, filename):
        if filename in ['script.js', 'styles.css']:
            route_dir = os.path.join(ROUTES_DIR, route_path)
            if os.path.exists(os.path.join(route_dir, filename)):
                return app.send_static_file(os.path.join(route_path, filename))
        return "", 404