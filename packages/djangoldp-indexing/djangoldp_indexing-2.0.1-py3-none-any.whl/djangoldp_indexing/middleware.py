class PortAwareHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_HOST' in request.META and ':' not in request.META['HTTP_HOST']:
            port = request.META.get('SERVER_PORT', '')
            if port and port != '80' and port != '443':
                request.META['HTTP_HOST'] = f"{request.META['HTTP_HOST']}:{port}"
        
        response = self.get_response(request)
        return response 