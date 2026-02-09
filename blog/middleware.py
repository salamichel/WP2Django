from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect

from blog.models import Redirect


class WPRedirectMiddleware:
    """Redirect old WordPress URLs to their new Django equivalents.

    Handles both path-based redirects (/old-page/) and WordPress
    query parameter redirects (?p=42, ?page_id=219, ?cat=71, ?tag=python).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Try path-based redirect first
        path = request.path
        redirect = self._find_redirect(path)

        # Try full path with query string (e.g. /?p=42)
        if not redirect and request.META.get("QUERY_STRING"):
            full_path = f"{path}?{request.META['QUERY_STRING']}"
            redirect = self._find_redirect(full_path)

        if redirect:
            if redirect.is_permanent:
                return HttpResponsePermanentRedirect(redirect.new_path)
            return HttpResponseRedirect(redirect.new_path)

        return self.get_response(request)

    def _find_redirect(self, path):
        try:
            return Redirect.objects.get(old_path=path)
        except Redirect.DoesNotExist:
            return None
