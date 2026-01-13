"""
Custom logging handler that sends logs to Observo platform
"""

import logging
import requests
import json
import threading
import queue
from datetime import datetime
from typing import Optional


class ObservoHandler(logging.Handler):
    """
    Logging handler that sends log records to Observo platform
    
    Usage in Django settings.py:
        LOGGING = {
            'handlers': {
                'observo': {
                    'class': 'observo_handler.ObservoHandler',
                    'level': 'INFO',
                    'project_id': 'your-project-id',
                    'api_key': 'your-api-key',
                    'observo_url': 'https://observo.yourdomain.com/api/v1/ingest/',
                },
            },
            'loggers': {
                'django': {
                    'handlers': ['observo', 'console'],
                    'level': 'INFO',
                },
            },
        }
    """
    
    def __init__(
        self,
        project_id: str,
        api_key: str,
        observo_url: str,
        batch_size: int = 10,
        flush_interval: int = 5,
        level=logging.NOTSET
    ):
        """
        Initialize Observo handler
        
        Args:
            project_id: Observo project ID
            api_key: Observo API key
            observo_url: Observo API endpoint URL
            batch_size: Number of logs to batch before sending
            flush_interval: Seconds between automatic flushes
            level: Minimum log level to capture
        """
        super().__init__(level)
        
        self.project_id = project_id
        self.api_key = api_key
        self.observo_url = observo_url
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        # Thread-safe queue for log records
        self.log_queue = queue.Queue()
        
        # Batch storage
        self.batch = []
        self.batch_lock = threading.Lock()
        
        # Running flag
        self.running = True
        
        # Start background worker thread
        self.worker_thread = threading.Thread(
            target=self._worker,
            daemon=True,
            name='ObservoHandlerWorker'
        )
        self.worker_thread.start()
        
        # Start periodic flush thread
        self.flush_thread = threading.Thread(
            target=self._periodic_flush,
            daemon=True,
            name='ObservoHandlerFlusher'
        )
        self.flush_thread.start()
    
    def emit(self, record: logging.LogRecord):
        """
        Emit a log record (called by logging framework)
        
        Args:
            record: LogRecord instance to send to Observo
        """
        try:
            # Convert LogRecord to Observo format
            log_entry = self._format_log_entry(record)
            
            # Add to queue (non-blocking)
            self.log_queue.put_nowait(log_entry)
        
        except Exception:
            # Fail silently - don't break the application
            self.handleError(record)
    
    def _format_log_entry(self, record: logging.LogRecord) -> dict:
        """
        Convert LogRecord to Observo API format
        
        Args:
            record: LogRecord to convert
            
        Returns:
            Dict in Observo API format
        """
        # Base log entry
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'message': self.format(record),
            'logger_name': record.name,
            'module': record.module,
            'function': record.funcName,
            'line_number': record.lineno,
        }
        
        # Add request_id if available (from middleware)
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        # Add user_id if available
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = str(record.user_id)
        
        # Add stack trace for errors
        if record.exc_info:
            log_entry['stack_trace'] = self.formatter.formatException(record.exc_info) if self.formatter else str(record.exc_info)
        
        # Additional metadata
        log_entry['metadata'] = {
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process,
            'pathname': record.pathname,
        }
        
        # Add custom fields
        if hasattr(record, 'extra_data'):
            log_entry['metadata'].update(record.extra_data)
        
        return log_entry
    
    def _worker(self):
        """Background worker that batches and sends logs"""
        while self.running:
            try:
                # Get log from queue (blocking with timeout)
                log_entry = self.log_queue.get(timeout=1.0)
                
                with self.batch_lock:
                    self.batch.append(log_entry)
                    
                    # Send batch if size reached
                    if len(self.batch) >= self.batch_size:
                        self._send_batch()
            
            except queue.Empty:
                continue
            except Exception:
                pass
    
    def _periodic_flush(self):
        """Periodically flush logs even if batch not full"""
        import time
        
        while self.running:
            time.sleep(self.flush_interval)
            self.flush()
    
    def _send_batch(self):
        """Send current batch to Observo (must be called with batch_lock held)"""
        if not self.batch:
            return
        
        headers = {
            'X-Project-ID': self.project_id,
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {'logs': self.batch.copy()}
        
        try:
            response = requests.post(
                self.observo_url,
                headers=headers,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 201:
                # Success - clear batch
                self.batch.clear()
            else:
                # Failed - clear batch to avoid memory buildup
                # In production, you might want to implement retry logic
                self.batch.clear()
        
        except requests.exceptions.RequestException:
            # Network error - clear batch to avoid memory buildup
            self.batch.clear()
    
    def flush(self):
        """Flush any remaining logs in batch"""
        with self.batch_lock:
            self._send_batch()
    
    def close(self):
        """Close handler and flush remaining logs"""
        self.running = False
        self.flush()
        super().close()