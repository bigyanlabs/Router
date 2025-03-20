/**
 * Log Viewer - Real-time log streaming and management
 */
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const logContainer = document.getElementById('log-container');
    const fileList = document.getElementById('file-list');
    const refreshFilesBtn = document.getElementById('refresh-files');
    const fileSearch = document.getElementById('file-search');
    const logSearch = document.getElementById('log-search');
    const searchResults = document.getElementById('search-results');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const downloadBtn = document.getElementById('download-btn');
    const autoScrollBtn = document.getElementById('auto-scroll');
    const clearLogsBtn = document.getElementById('clear-logs');
    const currentFileEl = document.getElementById('current-file');
    const fileStatsEl = document.getElementById('file-stats');
    const statusText = document.getElementById('status-text');
    const entryCounter = document.getElementById('entry-counter');
    const connectionStatus = document.getElementById('connection-status');

    // Templates
    const logEntryTemplate = document.getElementById('log-entry-template');
    const fileItemTemplate = document.getElementById('file-item-template');

    // State
    let currentFile = null;
    let entryCount = 0;
    let eventSource = null;
    let autoScroll = true;
    let currentFilter = 'all';
    let logEntries = [];
    let logFiles = [];
    
    // Initialize
    init();

    /**
     * Initialize the application
     */
    function init() {
        // Set up event listeners
        setupEventListeners();
        
        // Load log files
        loadLogFiles();
        
        // Connect to SSE stream
        connectEventSource();
        
        // Set status
        updateStatus('Initializing...');
    }

    /**
     * Set up event listeners for UI components
     */
    function setupEventListeners() {
        // Refresh files button
        refreshFilesBtn.addEventListener('click', () => {
            loadLogFiles();
        });

        // File search
        fileSearch.addEventListener('input', filterFiles);

        // Log search
        logSearch.addEventListener('input', filterLogs);
        
        // Filter buttons
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                currentFilter = button.dataset.level;
                filterLogs();
            });
        });

        // Download button
        downloadBtn.addEventListener('click', () => {
            if (currentFile) {
                window.location.href = `/api/download/${currentFile}`;
            }
        });

        // Auto-scroll toggle
        autoScrollBtn.addEventListener('click', () => {
            autoScroll = !autoScroll;
            autoScrollBtn.classList.toggle('active', autoScroll);
            if (autoScroll) {
                scrollToBottom();
            }
        });

        // Clear logs button
        clearLogsBtn.addEventListener('click', () => {
            clearLogs();
        });
    }

    /**
     * Connect to Server-Sent Events stream
     */
    function connectEventSource() {
        if (eventSource) {
            eventSource.close();
        }

        eventSource = new EventSource('/api/stream');
        
        eventSource.onopen = () => {
            updateConnectionStatus(true);
            updateStatus('Connected to log stream');
        };
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.connected) {
                updateConnectionStatus(true);
                return;
            }
            
            // Process log entries
            data.forEach(entry => {
                processLogEntry(entry);
            });
        };
        
        eventSource.onerror = () => {
            updateConnectionStatus(false);
            updateStatus('Connection lost. Reconnecting...');
            
            // Try to reconnect after a delay
            setTimeout(() => {
                if (eventSource.readyState === EventSource.CLOSED) {
                    connectEventSource();
                }
            }, 5000);
        };
    }

    /**
     * Load the list of log files
     */
    function loadLogFiles() {
        fileList.innerHTML = '<div class="loading pulsate">Loading files...</div>';
        
        fetch('/api/files')
            .then(response => response.json())
            .then(files => {
                logFiles = files;
                renderFileList(files);
                
                if (files.length > 0 && !currentFile) {
                    selectFile(files[0].name);
                }
            })
            .catch(error => {
                fileList.innerHTML = `<div class="error">Error loading files: ${error.message}</div>`;
                console.error('Error loading log files:', error);
            });
    }

    /**
     * Render the file list in the sidebar
     */
    function renderFileList(files) {
        fileList.innerHTML = '';
        
        if (files.length === 0) {
            fileList.innerHTML = '<div class="no-files">No log files found</div>';
            return;
        }
        
        files.forEach(file => {
            const template = document.importNode(fileItemTemplate.content, true);
            const fileItem = template.querySelector('.file-item');
            
            // Set data
            fileItem.dataset.filename = file.name;
            fileItem.querySelector('.file-name').textContent = file.name;
            fileItem.querySelector('.file-size').textContent = formatBytes(file.size);
            fileItem.querySelector('.file-date').textContent = file.modified;
            
            // Highlight current file
            if (file.name === currentFile) {
                fileItem.classList.add('active');
            }
            
            // Click handler
            fileItem.addEventListener('click', () => {
                selectFile(file.name);
            });
            
            fileList.appendChild(fileItem);
        });
    }

    /**
     * Select a log file to view
     */
    function selectFile(filename) {
        if (currentFile === filename) return;
        
        currentFile = filename;
        
        // Update UI
        const fileItems = fileList.querySelectorAll('.file-item');
        fileItems.forEach(item => {
            item.classList.toggle('active', item.dataset.filename === filename);
        });
        
        currentFileEl.textContent = filename;
        downloadBtn.disabled = false;
        
        // Clear current logs
        clearLogs();
        
        // Load logs for selected file
        loadLogs(filename);
    }

    /**
     * Load logs for a specific file
     */
    function loadLogs(filename) {
        updateStatus(`Loading logs from ${filename}...`);
        logContainer.innerHTML = '<div class="loading pulsate">Loading logs...</div>';
        
        fetch(`/api/logs?file=${filename}`)
            .then(response => response.json())
            .then(entries => {
                clearLogs();
                entries.forEach(entry => {
                    processLogEntry(entry, false); // Don't scroll for initial load
                });
                updateStatus(`Loaded ${entries.length} log entries`);
                
                // Update counters
                updateEntryCount();
                
                // Scroll to bottom after initial load
                if (autoScroll) {
                    scrollToBottom();
                }
            })
            .catch(error => {
                logContainer.innerHTML = `<div class="error">Error loading logs: ${error.message}</div>`;
                updateStatus(`Error loading logs: ${error.message}`);
                console.error('Error loading logs:', error);
            });
    }

    /**
     * Process a log entry and add it to the display
     */
    function processLogEntry(entry, scroll = true) {
        // Skip entries from other files if a file is selected
        if (currentFile && entry.file && entry.file !== currentFile) {
            return;
        }
        
        // Create log entry element
        const template = document.importNode(logEntryTemplate.content, true);
        const logEntry = template.querySelector('.log-entry');
        
        // Set log level class
        if (entry.level) {
            logEntry.classList.add(entry.level);
            logEntry.querySelector('.log-level').textContent = entry.level;
            logEntry.querySelector('.log-level').classList.add(entry.level);
        } else {
            logEntry.querySelector('.log-level').remove();
        }
        
        // Set timestamp
        if (entry.timestamp) {
            logEntry.querySelector('.log-timestamp').textContent = entry.timestamp;
        } else {
            logEntry.querySelector('.log-timestamp').remove();
        }
        
        // Set file name
        if (entry.file) {
            logEntry.querySelector('.log-file').textContent = entry.file;
        } else {
            logEntry.querySelector('.log-file').remove();
        }
        
        // Set message
        let message = entry.message || entry.raw || '';
        
        // Check for tracebacks
        if (message.includes('Traceback (most recent call last)')) {
            const parts = message.split('Traceback (most recent call last)');
            logEntry.querySelector('.log-message').textContent = parts[0];
            
            const traceback = document.createElement('div');
            traceback.className = 'traceback';
            traceback.textContent = 'Traceback (most recent call last)' + parts[1];
            logEntry.querySelector('.log-message').appendChild(traceback);
        } else {
            logEntry.querySelector('.log-message').textContent = message;
        }
        
        // Apply current filter
        if (currentFilter !== 'all' && entry.level !== currentFilter) {
            logEntry.classList.add('hidden');
        }
        
        // Add to log container
        logContainer.appendChild(logEntry);
        
        // Store entry for searching/filtering
        logEntries.push({
            element: logEntry,
            text: (entry.timestamp || '') + ' ' + (entry.level || '') + ' ' + message,
            level: entry.level || 'none',
            file: entry.file || currentFile
        });
        
        // Update entry count
        entryCount++;
        updateEntryCount();
        
        // Auto-scroll
        if (scroll && autoScroll) {
            scrollToBottom();
        }
        
        // Remove welcome message if present
        const welcomeMessage = logContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
    }

    /**
     * Filter log entries based on search text
     */
    function filterLogs() {
        const searchText = logSearch.value.toLowerCase();
        let visibleCount = 0;
        
        logEntries.forEach(entry => {
            // Check if entry matches search and filter
            const matchesSearch = searchText === '' || entry.text.toLowerCase().includes(searchText);
            const matchesFilter = currentFilter === 'all' || entry.level === currentFilter;
            
            // Show/hide based on matches
            entry.element.classList.toggle('hidden', !(matchesSearch && matchesFilter));
            
            // Count visible entries
            if (matchesSearch && matchesFilter) {
                visibleCount++;
            }
        });
        
        // Update counter
        const hiddenCount = entryCount - visibleCount;
        if (hiddenCount > 0) {
            entryCounter.textContent = `${visibleCount} of ${entryCount} entries`;
        } else {
            entryCounter.textContent = `${entryCount} entries`;
        }
        
        // If auto-scroll enabled, scroll to bottom
        if (autoScroll) {
            scrollToBottom();
        }
    }

    /**
     * Filter file list based on search text
     */
    function filterFiles() {
        const searchText = fileSearch.value.toLowerCase();
        const fileItems = fileList.querySelectorAll('.file-item');
        
        fileItems.forEach(item => {
            const filename = item.dataset.filename.toLowerCase();
            item.style.display = filename.includes(searchText) ? '' : 'none';
        });
    }

    /**
     * Clear all log entries
     */
    function clearLogs() {
        logContainer.innerHTML = '';
        logEntries = [];
        entryCount = 0;
        updateEntryCount();
    }

    /**
     * Update the entry counter
     */
    function updateEntryCount() {
        entryCounter.textContent = `${entryCount} entries`;
    }

    /**
     * Update connection status indicator
     */
    function updateConnectionStatus(connected) {
        connectionStatus.className = connected 
            ? 'connection-status connected' 
            : 'connection-status disconnected';
        
        connectionStatus.querySelector('.status-text').textContent = 
            connected ? 'Connected' : 'Disconnected';
    }

    /**
     * Update status text
     */
    function updateStatus(text) {
        statusText.textContent = text;
    }

    /**
     * Format bytes to human readable size
     */
    function formatBytes(bytes, decimals = 1) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    /**
     * Scroll to the bottom of the log container
     */
    function scrollToBottom() {
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    /**
     * Handle visibility change to reconnect when tab becomes visible
     */
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible' && 
            (!eventSource || eventSource.readyState === EventSource.CLOSED)) {
            connectEventSource();
        }
    });

    /**
     * Clean up event source on page unload
     */
    window.addEventListener('beforeunload', () => {
        if (eventSource) {
            eventSource.close();
        }
    });
});