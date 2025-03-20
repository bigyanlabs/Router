import os
from flask import Flask, request, session, render_template_string, current_app
import logging

ROUTES_DIR = "routes"
LAYOUT_PATH = os.path.join(ROUTES_DIR, "_layout.html")

def setup(app: Flask) -> None:
    """Configure the template engine to use route-specific templates"""
    
    @app.context_processor
    def inject_template_helpers():
        """Inject useful variables and helpers into templates"""
        route = request.path.strip('/')
        if not route:
            route = ''  
            
        route_dir = os.path.join(ROUTES_DIR, route)
        
        css_exists = os.path.exists(os.path.join(route_dir, "styles.css"))
        js_exists = os.path.exists(os.path.join(route_dir, "script.js"))
        css_path = f"/{route}/styles.css" if route else "/styles.css"
        js_path = f"/{route}/script.js" if route else "/script.js"
        
        user_from_session = session.get('user')
        user_from_cookie = request.cookies.get('user')
        is_authenticated = bool(user_from_session or user_from_cookie)
        
        print(f"CSS exists: {css_exists}, JS exists: {js_exists}")
        print(f"CSS path: {css_path}, JS path: {js_path}")
            
        return {
            'script_url': js_path if js_exists else None,
            'style_url': css_path if css_exists else None,
            'current_route': route or 'index',
            'is_authenticated': is_authenticated,
            'user': user_from_session or user_from_cookie
        }
    
    original_get_template = app.jinja_env.get_template
    
    def get_route_template(name, parent=None, globals=None):
        """Custom template loader that checks route-specific directories first"""
        try:
            if request and name == "page.html":
                route = request.path.strip('/')
                route_dir = route.replace('/', os.sep)
                
                template_path = os.path.join(ROUTES_DIR, route_dir, name)
                
                layout_exists = os.path.exists(LAYOUT_PATH)
                print(f"Layout exists: {layout_exists}, path: {LAYOUT_PATH}")
                
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        has_html_structure = "<html" in content.lower() and "</html>" in content.lower()

                        print(f"Loading template from: {template_path}")
                        print(f"Template has HTML structure: {has_html_structure}")
                        
                        if not has_html_structure and layout_exists:
                            with open(LAYOUT_PATH, 'r', encoding='utf-8') as layout_file:
                                layout = layout_file.read()
                                
                                print(f"Layout content length: {len(layout)}")
                                print(f"Layout has placeholder: {'{{ content }}' in layout}")
                               
                                if "{{ content }}" in layout:
                                    content = layout.replace("{{ content }}", content)
                                    print("Replaced {{ content }} in layout")
                                else:
                                    print("No {{ content }} placeholder found, using default layout")
                                    content = f'''
                                    <!DOCTYPE html>
                                    <html>
                                    <head>
                                        <meta charset="UTF-8">
                                        <title>{{{{ title|default('Page Title') }}}}</title>
                                        <link rel="stylesheet" href="{'/styles.css' if not route else f'/{route}/styles.css'}">
                                    </head>
                                    <body>
                                        {content}
                                        <script src="{'/script.js' if not route else f'/{route}/script.js'}"></script>
                                    </body>
                                    </html>
                                    '''
                        print(f"Final template size: {len(content)} characters")
                        template = app.jinja_env.from_string(content)
                        template.filename = template_path  
                        return template
                        
        except (RuntimeError, AttributeError) as e:
            app.logger.error(f"Template engine error: {str(e)}")
            print(f"Template engine error: {str(e)}")
            
        return original_get_template(name, parent, globals)
        
    app.jinja_env.get_template = get_route_template
    