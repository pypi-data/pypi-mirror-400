from django.conf import settings
from django.db.models import QuerySet, Q
from rest_framework.permissions import BasePermission
from djstripe.models.core import Customer
from djstripe.models.billing import Subscription, SubscriptionItem, Plan
from djangoldp.models import Model
from djangoldp.utils import is_authenticated_user


def _get_customer_for_user(user):
    # get the customer using the user's email
    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp-stripe/-/issues/1
    user_customer = Customer.objects.filter(email=user.email)
    if not user_customer.exists():
        return None
    
    return user_customer[0]


def user_has_any_active_subscription(user):
    customer = _get_customer_for_user(user)
    
    if customer is None:
        return False
    
    return customer.has_any_active_subscription()


def user_has_subscriptions_in_products_list(user, products):
    '''
    :param products: a set of product ids which the user must be subscribed to
    '''

    user_customer = _get_customer_for_user(user)
    if user_customer is None:
        return False
    
    # fetch the products which the user is subscribed to
    user_subscriptions = [s.id for s in user_customer._get_valid_subscriptions()]
    user_subscriptions = SubscriptionItem.objects.filter(subscription__in=user_subscriptions)
    user_plan_ids = [i.plan for i in user_subscriptions]
    user_products = set(Plan.objects.filter(id__in=user_plan_ids).values_list('product', flat=True))

    # reject if there are any required products missing from the user
    if len(products.difference(user_products)) > 0:
        return False
    
    return True


def user_has_subscriptions_for_model(user, model):
    '''
    :return: True if the user has subscriptions on all of the required products for a given model
    '''
    if not is_authenticated_user(user):
        return False
    
    # fetch the required products from the model
    required_product_ids = set(Model.get_meta(model, 'PERMS_REQUIRED_STRIPE_SUBSCRIPTIONS', []))

    if len(required_product_ids) == 0:
        return True

    return user_has_subscriptions_in_products_list(user, required_product_ids)


class StripeSubscriptionPermissions(BasePermission):
    '''
    Permissions that require that the requesting user is subscribed to all required products that are configured on the model
    '''
    def has_permission(self, request, view):
        if not hasattr(view, 'model'):
            return False
        
        return user_has_subscriptions_for_model(request.user, view.model)
    
    def has_object_permission(self, request, view, obj):
        return user_has_subscriptions_for_model(request.user, type(obj))        
