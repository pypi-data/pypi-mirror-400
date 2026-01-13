import pytest
from espy_pay.general.enums import TranxEnum,ISPEnum
from espy_pay.general.schema import TranxDto
from pydantic import ValidationError
def test_tranx_dto_valid():
    # Test creating a valid TranxDto instance
    tranx_data = {
        "amount": 2500,
        "currency": "NGN",
        "description": "Payment for goods",
        "status": TranxEnum.PENDING,
        "isp": ISPEnum.STRIPE,
        "stripe_payment_method": "pm_test",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
    }
    tranx_dto = TranxDto(**tranx_data)
    assert tranx_dto.amount == 2500
    assert tranx_dto.currency == "USD"  # Currency should be USD as per check_stripe validator

def test_tranx_dto_invalid_amount():
    # Test creating a TranxDto instance with invalid amount
    tranx_data = {
        "amount": 1500,  # Invalid amount, less than 2000
        "currency": "NGN",
        "status": TranxEnum.PENDING,
        "isp": ISPEnum.STRIPE,
        "stripe_payment_method": "pm_test"
    }
    with pytest.raises(ValidationError):
        TranxDto(**tranx_data)

def test_tranx_dto_without_email_or_phone():
    # Test creating a TranxDto instance without email or phone when payee_id is not provided
    tranx_data = {
        "amount": 2500,
        "currency": "NGN",
        "status": TranxEnum.PENDING,
        "isp": ISPEnum.STRIPE,
        "stripe_payment_method": "pm_test",
        "first_name": "John",
        "last_name": "Doe"
        # Missing email
    }
    with pytest.raises(ValidationError):
        TranxDto(**tranx_data)

def test_tranx_dto_without_stripe_payment_method():
    # Test creating a TranxDto instance without stripe_payment_method for Stripe ISP
    tranx_data = {
        "amount": 2500,
        "currency": "NGN",
        "status": TranxEnum.PENDING,
        "isp": ISPEnum.STRIPE
        # Missing stripe_payment_method
    }
    with pytest.raises(ValidationError):
        TranxDto(**tranx_data)

