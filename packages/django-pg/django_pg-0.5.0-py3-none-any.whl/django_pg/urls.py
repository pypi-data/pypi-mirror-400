from django.urls import path
from django.conf import settings
from .views import StripeWebhookView

stripe_webhook_path = getattr(settings, "DJANGO_PG_STRIPE_WEBHOOK_PATH", "webhooks/stripe/")

urlpatterns = [
    path(stripe_webhook_path, StripeWebhookView.as_view(), name="stripe_webhook"),
]
