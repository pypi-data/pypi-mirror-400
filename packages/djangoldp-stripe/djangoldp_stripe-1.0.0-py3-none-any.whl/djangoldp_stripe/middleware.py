from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.urls import reverse

from djangoldp.utils import is_authenticated_user
from djangoldp_stripe.permissions import user_has_any_active_subscription


include_paths = getattr(settings, 'INCLUDE_FROM_GLOBAL_STRIPE_SUBSCRIPTION_REQ', [])


class StripeSubscriptionRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _request_path_included(self, request):
        return request.path in include_paths

    def __call__(self, request):
        if is_authenticated_user(request.user) and self._request_path_included(request):

            if not user_has_any_active_subscription(request.user):
                raise PermissionDenied('user must be subscribed to required products to access this site')
        
        return self.get_response(request)
