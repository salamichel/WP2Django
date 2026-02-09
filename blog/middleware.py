from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect

from blog.models import Redirect


class WPRedirectMiddleware:
    """Redirect old WordPress URLs to their new Django equivalents."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        try:
            redirect = Redirect.objects.get(old_path=path)
            if redirect.is_permanent:
                return HttpResponsePermanentRedirect(redirect.new_path)
            return HttpResponseRedirect(redirect.new_path)
        except Redirect.DoesNotExist:
            pass
        return self.get_response(request)
