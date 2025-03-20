import os
import sys
import time
import json
import logging
import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flask import Flask, render_template, jsonify, request, Response, send_from_directory


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

ROOT_DIR = Path(__file__).parent.parent
LOGS_DIR = ROOT_DIR / "ROUTER" / "logs"
TEMPLATES_DIR = ROOT_DIR / "ROUTER"

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)


if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR)

log_server = Flask(__name__, 
                  static_folder=str(TEMPLATES_DIR),  
                  static_url_path='',                
                  template_folder=str(TEMPLATES_DIR)) 
print("Hello")
print(log_server.static_folder)
clients = []

class LogFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_position = {}
        self.active_logs = {}
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.log'):
            log_file = event.src_path
            
            if log_file not in self.last_position:
                self.last_position[log_file] = 0
                
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                   
                    f.seek(self.last_position[log_file])
                    
                    
                    new_content = f.read()
                    
                    if new_content:
                        
                        self.last_position[log_file] = f.tell()
                        
        
                        self._process_and_broadcast(log_file, new_content)
            except Exception as e:
                logging.error(f"Error reading log file {log_file}: {str(e)}")
    
    def _process_and_broadcast(self, log_file, content):
        """Process log content and broadcast to clients"""
        log_name = os.path.basename(log_file)
        
        # Process entries
        entries = []
        for line in content.splitlines():
            if not line.strip():
                continue
                
            entry = {"raw": line, "file": log_name}
            
            # Parse timestamp
            timestamp_match = line[:19] if len(line) >= 19 else None
            if timestamp_match:
                entry["timestamp"] = timestamp_match
            
            # Parse log level
            if " - [INFO] - " in line:
                entry["level"] = "info"
                entry["message"] = line.split(" - [INFO] - ", 1)[1]
            elif " - [ERROR] - " in line:
                entry["level"] = "error"
                entry["message"] = line.split(" - [ERROR] - ", 1)[1]
            elif " - [WARNING] - " in line:
                entry["level"] = "warning"
                entry["message"] = line.split(" - [WARNING] - ", 1)[1]
            elif " - [DEBUG] - " in line:
                entry["level"] = "debug"
                entry["message"] = line.split(" - [DEBUG] - ", 1)[1]
            else:
                entry["level"] = "none"
                entry["message"] = line
            
            entries.append(entry)
        
        if entries:
           
            self._send_to_clients(entries)
    
    def _send_to_clients(self, entries):
        """Send log entries to all connected clients"""
       
        data = json.dumps(entries)
        message = f"data: {data}\n\n"
        
       
        for client in list(clients):
            try:
                client.put(message)
            except Exception:
                clients.remove(client)
    
    def read_initial_logs(self, log_file=None):
        """Read initial log content for new connections"""
        entries = []
        
        
        if log_file and os.path.exists(log_file):
            files_to_read = [log_file]
        else:
            
            files_to_read = sorted(
                [os.path.join(LOGS_DIR, f) for f in os.listdir(LOGS_DIR) if f.endswith('.log')],
                key=os.path.getmtime, 
                reverse=True  
            )
        
        for file_path in files_to_read:
            try:
               
                if file_path not in self.last_position:
                    self.last_position[file_path] = os.path.getsize(file_path)
                
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                log_name = os.path.basename(file_path)
                
               
                for line in content.splitlines():
                    if not line.strip():
                        continue
                        
                    entry = {"raw": line, "file": log_name}
                    
                  
                    timestamp_match = line[:19] if len(line) >= 19 else None
                    if timestamp_match:
                        entry["timestamp"] = timestamp_match
                    
                    
                    if " - [INFO] - " in line:
                        entry["level"] = "info"
                        entry["message"] = line.split(" - [INFO] - ", 1)[1]
                    elif " - [ERROR] - " in line:
                        entry["level"] = "error"
                        entry["message"] = line.split(" - [ERROR] - ", 1)[1]
                    elif " - [WARNING] - " in line:
                        entry["level"] = "warning"
                        entry["message"] = line.split(" - [WARNING] - ", 1)[1]
                    elif " - [DEBUG] - " in line:
                        entry["level"] = "debug"
                        entry["message"] = line.split(" - [DEBUG] - ", 1)[1]
                    else:
                        entry["level"] = "none"
                        entry["message"] = line
                    
                    entries.append(entry)
            
            except Exception as e:
                logging.error(f"Error reading log file {file_path}: {str(e)}")
                entries.append({
                    "level": "error",
                    "message": f"Error reading log file {os.path.basename(file_path)}: {str(e)}",
                    "file": os.path.basename(file_path),
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return entries

log_handler = LogFileHandler()

@log_server.route('/')
def index():
    """Main page of the log viewer"""
    return render_template('logger.html')

@log_server.route('/api/logs')
def get_logs():
    """API endpoint to get all logs"""
    log_file = request.args.get('file')
    if log_file:
        log_path = os.path.join(LOGS_DIR, log_file)
    else:
        log_path = None
        
    entries = log_handler.read_initial_logs(log_path)
    return jsonify(entries)

@log_server.route('/api/files')
def get_log_files():
    """API endpoint to get list of log files"""
    log_files = []
    if os.path.exists(LOGS_DIR):
        for file in os.listdir(LOGS_DIR):
            if file.endswith('.log'):
                file_path = os.path.join(LOGS_DIR, file)
                log_files.append({
                    'name': file,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        log_files.sort(key=lambda x: x['modified'], reverse=True)
    
    return jsonify(log_files)

@log_server.route('/api/stream')
def stream_logs():
    """Server-sent events endpoint for real-time log streaming"""
    def generate():
        queue = []
        clients.append(queue)
        
        try:
            yield "data: {\"connected\": true}\n\n"
            
            while True:
                if queue and len(queue) > 0:
                    yield queue.pop(0)
                else:
                    time.sleep(0.1)
        except GeneratorExit:
            if queue in clients:
                clients.remove(queue)
    
    return Response(generate(), mimetype='text/event-stream')

@log_server.route('/api/download/<filename>')
def download_log(filename):
    """Download a log file"""
    return send_from_directory(LOGS_DIR, filename, as_attachment=True)

@log_server.route('/api/search')
def search_logs():
    """Search within log files"""
    query = request.args.get('q', '').lower()
    log_file = request.args.get('file')
    
    if not query:
        return jsonify([])
    
    results = []
    if log_file:
        files_to_search = [os.path.join(LOGS_DIR, log_file)]
    else:
        files_to_search = [os.path.join(LOGS_DIR, f) for f in os.listdir(LOGS_DIR) if f.endswith('.log')]
    
    for file_path in files_to_search:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                line_num = 0
                for line in f:
                    line_num += 1
                    if query in line.lower():
                        file_name = os.path.basename(file_path)
                        results.append({
                            'file': file_name,
                            'line': line_num,
                            'content': line.strip()
                        })
        except Exception as e:
            logging.error(f"Error searching log file {file_path}: {str(e)}")
    
    return jsonify(results)

def start(host='0.0.0.0', port=9001):
    """Start the log server and file watcher"""
    # Set up file watcher
    event_handler = log_handler
    observer = Observer()
    observer.schedule(event_handler, str(LOGS_DIR), recursive=False)
    observer.start()
    
    try:
        logging.info(f"Log server starting on http://{host}:{port}")
        log_server.run(host=host, port=port, threaded=True,debug=True)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()


if __name__ == "__main__":
    port = 9001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    start(port=port)

