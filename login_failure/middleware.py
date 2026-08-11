from login_failure.signals import request_accessor


class RequestProviderError(Exception):
    pass


class RequestProvider:
    def __init__(self, get_response):
        self._request = None
        self.get_response = get_response
        request_accessor.connect(self._provide_request)

    def __call__(self, request):
        self._request = request
        return self.get_response(request)

    def _provide_request(self, **kwargs):
        return self._request
