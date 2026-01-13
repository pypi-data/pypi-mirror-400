"""Copyright 2024 Everlasting Systems and Solutions LLC (www.myeverlasting.net).
All Rights Reserved.

No part of this software or any of its contents may be reproduced, copied, modified or adapted, without the prior written consent of the author, unless otherwise indicated for stand-alone materials.

For permission requests, write to the publisher at the email address below:
office@myeverlasting.net

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List
from espy_pay.ng.paystack.util.Bankcodes import BankCode


class Response(BaseModel):
    status: bool
    message: str
    data: object


# class TranxRequest(BaseModel):
#     email: EmailStr
#     amount: int = Field(..., gt=2500, description="Amount must be greater than 2500 kobo")
#     authorization_code: Optional[str] = None
#     reference: Optional[int] = None
#     currency: Optional[str] = None
#     callback_url: Optional[AnyHttpUrl] = None
class Subaccount(BaseModel):
    subaccount: str = Field(
        ..., min_length=5, description="Subaccount charged code from Paystack"
    )
    share: int


class SplitRequest(BaseModel):
    name: str
    type: str = Field(..., description="Type must be either 'percentage' or 'flat'")
    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
        pattern="^[A-Z]{3}$",
        description="Currency must be a 3-letter code",
    )
    subaccounts: List[Subaccount]
    bearer_type: str
    bearer_subaccount: str


class SplitFlatFee(BaseModel):
    email: EmailStr = Field(..., description="Email of the user to be charged")
    amount: int = Field(
        ..., gt=2500, description="Amount must be greater than 2500 kobo"
    )
    subaccount: str = Field(
        ..., min_length=5, description="Subaccount charged code from Paystack"
    )
    transaction_charge: int = Field(..., gt=0, description="Transaction charge in kobo")


class Subaccount_Request(BaseModel):
    business_name: str
    settlement_bank: str = Field(..., description="Bank code from Paystack Bankcodes")
    account_number: str
    percentage_charge: float

    @field_validator("settlement_bank")
    def validate_bank_code(cls, v):
        valid_codes = [bank.value for bank in BankCode]
        if v not in valid_codes:
            raise ValueError(f"Invalid bank code. Must be one of: {valid_codes}")
        return v
