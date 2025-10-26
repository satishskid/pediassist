import sys
import os
import json
from urllib.parse import urlparse

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import the PediAssist application
from pediassist.web_app import app

def handler(event, context):
    """
    Netlify Functions handler for PediAssist application
    """
    
    # Extract request details
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    query_params = event.get('queryStringParameters', {})
    body = event.get('body', '')
    
    # Create WSGI environment
    environ = {
        'REQUEST_METHOD': http_method,
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join([f"{k}={v}" for k, v in query_params.items()]) if query_params else '',
        'SERVER_NAME': headers.get('host', 'pediassist-netlify.ap'),
        'SERVER_PORT': '443' if headers.get('x-forwarded-proto') == 'https' else '80',
        'wsgi.url_scheme': headers.get('x-forwarded-proto', 'https'),
        'wsgi.input': body.encode('utf-8') if body else b'',
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'wsgi.version': (1, 0),
    }
    
    # Add headers to environment
    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            key = f'HTTP_{key}'
        environ[key] = value
    
    # Handle response
    response_data = {}
    response_headers = []
    
    def start_response(status, headers):
        response_data['status'] = status
        response_data['headers'] = dict(headers)
        return lambda x: None  # Dummy write function
    
    # Call the Flask application
    try:
        response_body = app(environ, start_response)
        
        # Collect response body
        body_content = b''
        for chunk in response_body:
            if isinstance(chunk, str):
                body_content += chunk.encode('utf-8')
            else:
                body_content += chunk
        
        # Return Netlify function response format
        return {
            'statusCode': int(response_data['status'].split()[0]),
            'headers': response_data['headers'],
            'body': body_content.decode('utf-8')
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/plain',
                'Access-Control-Allow-Origin': '*'
            },
            'body': f'Internal Server Error: {str(e)}'
        }