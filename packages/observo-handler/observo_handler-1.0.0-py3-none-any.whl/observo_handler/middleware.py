"""
Middleware to add request_id to all logs
"""

import uuid
import logging
from django.utils.deprecation import MiddlewareMixin


class RequestIDMiddleware(MiddlewareMixin):
    """
    Middleware that generates a unique request_id for each request
    and attaches it to all log records during that request
    """
    
    def process_request(self, request):
        """Generate request_id at start of request"""
        # Generate unique request ID
        request.request_id = str(uuid.uuid4())
        
        # Store old factory
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            
            # Add request_id to log record
            record.request_id = getattr(request, 'request_id', None)
            
            # Add user_id if authenticated
            if hasattr(request, 'user') and request.user.is_authenticated:
                record.user_id = request.user.id
            
            return record
        
        # Set new factory for this request
        logging.setLogRecordFactory(record_factory)
        
        return None
    
    def process_response(self, request, response):
        """Optionally add request_id to response headers"""
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id
        
        # Reset to old factory
        logging.setLogRecordFactory(logging.LogRecord)
        
        return response