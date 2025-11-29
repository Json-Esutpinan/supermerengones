from django.utils.deprecation import MiddlewareMixin

class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Basic hardening headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=()'
        # Minimal CSP allowing same-origin resources; adjust as needed
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        if request.is_secure():
            # Only set HSTS over HTTPS
            response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains'
        return response
