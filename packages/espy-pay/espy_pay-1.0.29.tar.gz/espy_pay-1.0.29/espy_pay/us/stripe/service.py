import stripe
from espy_pay.us.stripe.CONSTANTS import STRIPE_KEY
from espy_pay.general.schema import TranxDto
import logging
logger = logging.getLogger(__name__)
async def create_stripe(data: TranxDto):
    """
    This function creates a payment intent on Stripe.
    Args:
        data (dict): A dictionary containing the payment data.
    """
    try:
        stripe.api_key = STRIPE_KEY
        intent = stripe.PaymentIntent.create(
            amount=data.amount,
            currency=data.currency,
            description=data.description,
            automatic_payment_methods={"enabled": True},
            metadata={"ref": data.ref}
        )
        logger.info(f"Payment intent created: {intent}")
        return intent
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise e
async def confirm_stripe(intent_id: str, payment_method: str, callback: str, name: str):
    """
    This function confirms a payment intent on Stripe.
    Args:
        data (dict): A dictionary containing the payment data.
    """
    try:
        stripe.api_key = STRIPE_KEY
        intent = stripe.PaymentIntent.confirm(
            intent=intent_id,
            payment_method=payment_method,
            return_url=callback
        )
        logger.info(f"Payment intent confirmed: {intent}")
        return intent
    except Exception as e:
        logger.error(f"Error confirming payment intent: {e}")
        raise e
async def retrieve_intent(id: str):
    """
    This function retrieves a payment intent on Stripe.
    Args:
        data (dict): A dictionary containing the payment data.
    """
    try:
        stripe.api_key = STRIPE_KEY
        intent = stripe.PaymentIntent.retrieve(
            id
        )
        logger.info(f"Payment intent retrieved: {intent}")
        return intent
    except Exception as e:
        logger.error(f"Error retrieving payment intent: {e}")
        raise e
async def modify_intent(id: str,data: dict):
    """
    This function modifies a payment intent on Stripe.
    Args:
        data (dict): A dictionary containing the payment data.
    """
    try:
        stripe.api_key = STRIPE_KEY
        intent = stripe.PaymentIntent.modify(
            id,
            **data
        )
        logger.info(f"Payment intent modified: {intent}")
        return intent
    except Exception as e:
        logger.error(f"Error modifying payment intent: {e}")
        raise e