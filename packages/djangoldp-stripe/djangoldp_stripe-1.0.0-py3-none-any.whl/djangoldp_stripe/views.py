from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from djangoldp.views import NoCSRFAuthentication
from rest_framework import status
from rest_framework.views import APIView, Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import permission_classes 
from djstripe.models.core import Price, Product
from djstripe.models.billing import Subscription, SubscriptionItem, Plan
import stripe

from djangoldp.views import LDPAPIView, JSONLDRenderer
from djangoldp.serializers import LDPSerializer
from djangoldp.utils import is_anonymous_user
from djangoldp_stripe.permissions import user_has_any_active_subscription, _get_customer_for_user

STRIPE_LIVE_SECRET_KEY = settings.STRIPE_LIVE_SECRET_KEY
STRIPE_LIVE_MODE = settings.STRIPE_LIVE_MODE
STRIPE_TEST_SECRET_KEY = settings.STRIPE_TEST_SECRET_KEY

stripe.api_key = STRIPE_LIVE_SECRET_KEY if STRIPE_LIVE_MODE else STRIPE_TEST_SECRET_KEY


class SuccessPageView(APIView):
    authentication_classes = (NoCSRFAuthentication,)

    def get(self, request):
        return render(request, 'success.html')


class CancelledPageView(APIView):
    authentication_classes = (NoCSRFAuthentication,)

    def get(self, request):
        return render(request, 'cancel.html')


class CheckoutSessionView(APIView):
    authentication_classes = (NoCSRFAuthentication,)

    def resolve_price(self, price_id, lookup_key):
        # lookup_key or id must be passed in the requesting form
        if price_id is None:
            if lookup_key is None:
                raise ValidationError('lookup_key or price is required')

            return get_object_or_404(Price, lookup_key=lookup_key)
        
        return get_object_or_404(Price, id=price_id)

    def get(self, request):
        price_id = request.GET.get('price_id', None)
        lookup_key = request.GET.get('lookup_key', None)

        price = self.resolve_price(price_id, lookup_key)

        return render(request, 'checkout.html', context={'product': price.product, 'price': price, 'unit_amount': price.unit_amount * 0.01})

    def post(self, request):
        # lookup_key or id must be passed in the requesting form
        price_id = request.data.get('price_id', None)
        lookup_key = request.data.get('lookup_key', None)

        price = self.resolve_price(price_id, lookup_key)
        host_url = settings.SITE_URL

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price.id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=host_url + '/checkout-session/success/',
            cancel_url=host_url + '/checkout-session/cancel/',
        )
        return redirect(checkout_session.url)


class UserSubscriptionView(LDPAPIView):
    renderer_classes = [JSONLDRenderer,]

    def get(self, request):
        if is_anonymous_user(request.user):
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        user_customer = _get_customer_for_user(request.user)
        user_subscriptions = [s.id for s in user_customer._get_valid_subscriptions()]
        user_subscriptions = SubscriptionItem.objects.filter(subscription__in=user_subscriptions)
        user_plan_ids = [i.plan for i in user_subscriptions]
        user_products = set(Plan.objects.filter(id__in=user_plan_ids).values_list('product', flat=True))
        user_products = Product.objects.filter(id__in=user_products)

        # TODO: this should be done with a serializer class
        # https://git.startinblox.com/djangoldp-packages/djangoldp/-/issues/277
        serialized_products = []
        for product in user_products:
            serialized_products.append({
                "name": product.name,
                "id": product.id
            })

        data = {
            "@context": settings.LDP_RDF_CONTEXT,
            "@type":"ldp:Container",
            "@id": '{}{}'.format(settings.SITE_URL, reverse('stripe-user-subscriptions')),
            "ldp:contains": serialized_products
        }

        return Response(data, status=status.HTTP_200_OK)


class UserHasValidSubscriptionView(LDPAPIView):

    def get(self, request):
        if is_anonymous_user(request.user):
            return Response(False, status=status.HTTP_401_UNAUTHORIZED)

        if user_has_any_active_subscription(request.user):
            return Response(True, status=status.HTTP_200_OK)
        
        redirect_url = getattr(settings, 'REDIRECT_URL_NO_SUBSCRIPTION', None)
        if redirect_url is not None:
            return redirect(redirect_url)
        
        return Response(False, status=status.HTTP_200_OK)
