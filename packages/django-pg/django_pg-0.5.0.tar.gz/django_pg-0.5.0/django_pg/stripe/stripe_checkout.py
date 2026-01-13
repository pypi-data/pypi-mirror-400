import stripe
from django.conf import settings
from ..exceptions import PaymentConfigurationError, PaymentRuntimeError

def create_stripe_checkout_session(*, order, success_url: str, cancel_url: str, customer_email: str | None = None,):
    if not success_url or not cancel_url:
        raise PaymentConfigurationError(
            "Both success_url and cancel_url must be provided for Stripe Checkout."
        )
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY

        amount = int(float(order.total_price) * 100)
        currency = getattr(settings, "STRIPE_CURRENCY", "usd")

        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            customer_email=customer_email,
            line_items=[
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": amount,
                        "product_data": {
                            "name": f"Order {order.order_reference}",
                        },
                    },
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "order_reference": order.order_reference,
            },
        )

        return session
    
    # ---- Stripe / network / runtime failures ----
    except stripe.error.StripeError as e:
        raise PaymentRuntimeError(
            f"Stripe checkout session creation failed: {str(e)}"
        ) from e