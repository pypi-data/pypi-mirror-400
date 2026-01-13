import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from ..utils import get_model
from ..exceptions import PaymentConfigurationError, PaymentRuntimeError


def _get_stripe_client():
    key = getattr(settings, "STRIPE_SECRET_KEY", None)
    if not key:
        raise PaymentConfigurationError("STRIPE_SECRET_KEY is not configured.")
    stripe.api_key = key
    return stripe


def construct_event(payload: bytes, sig_header: str | None):
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)
    if not webhook_secret:
        raise PaymentConfigurationError("STRIPE_WEBHOOK_SECRET is not configured.")

    if not sig_header:
        raise PaymentRuntimeError("Missing Stripe-Signature header.")

    try:
        return stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret,
        )
    except ValueError as e:
        # Invalid payload
        raise PaymentRuntimeError("Invalid Stripe webhook payload.") from e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise PaymentRuntimeError("Invalid Stripe webhook signature.") from e


def handle_event(event: dict) -> None:
    """
    Updates Order based on Stripe webhook events.
    """
    event_type = event.get("type")
    data_object = (event.get("data") or {}).get("object") or {}

    # We primarily care about Checkout success
    if event_type == "checkout.session.completed":
        # Checkout Session object
        metadata = data_object.get("metadata") or {}
        order_reference = metadata.get("order_reference")

        if not order_reference:
            # nothing we can link
            return

        Order = get_model("PAYMENT_ORDER_MODEL")
        order = Order.objects.filter(order_reference=order_reference).first()
        if not order:
            return

        # If already paid, ignore (idempotent)
        if getattr(order, "payment_made", False):
            return

        # Optional: you can also check payment_status == "paid"
        payment_status = data_object.get("payment_status")  # usually "paid"
        if payment_status and payment_status != "paid":
            return

        order.payment_made = True
        order.order_placed = True
        order.status = "Order Placed"
        order.payment_method = "stripe"
        order.payment_date = timezone.now()
        order.save()

        return


def stripe_webhook_response(request):
    """
    Django view handler (no DRF required).
    Returns HttpResponse.
    """
    # Ensure stripe module has API key (not strictly required for signature verify,
    # but useful if you later fetch objects)
    _get_stripe_client()

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    event = construct_event(payload, sig_header)
    handle_event(event)

    return HttpResponse(status=200)