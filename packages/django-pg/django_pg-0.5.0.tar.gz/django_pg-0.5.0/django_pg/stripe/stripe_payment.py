import stripe
from django.conf import settings
from django.utils import timezone
from ..utils import get_model, validate_user_for_payment, validate_payment_amount


def verify_stripe_payment(order_id, transaction_id, user):
    """
    transaction_id = Stripe Checkout Session ID (cs_...)
    """

    # Validate user
    validation = validate_user_for_payment(user)
    if not validation["success"]:
        return validation

    # Get Order model
    Order = get_model("PAYMENT_ORDER_MODEL")

    # Retrieve order
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return {"success": False, "message": "Order not found."}

    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)
    if not stripe.api_key:
        return {"success": False, "message": "Stripe is not configured."}

    # Retrieve Checkout Session from Stripe
    try:
        session = stripe.checkout.Session.retrieve(transaction_id)
    except Exception:
        return {"success": False, "message": "Error verifying Stripe payment"}

    # Confirm payment
    if session.payment_status == "paid":
        paid_amount = (session.amount_total or 0) / 100

        amount_validation = validate_payment_amount(order, paid_amount)
        if not amount_validation["success"]:
            return amount_validation

        # Update order
        order.payment_made = True
        order.order_placed = True
        order.status = "Order Placed"
        order.payment_method = "stripe"
        order.stripe_checkout_session_id = transaction_id
        order.payment_date = timezone.now()
        order.save()

        return {"success": True, "order_reference": order.order_reference}

    return {"success": False, "message": "Payment verification failed"}
