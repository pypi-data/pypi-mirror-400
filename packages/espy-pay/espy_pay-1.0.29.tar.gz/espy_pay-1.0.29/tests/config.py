import os
from dotenv import load_dotenv
load_dotenv()
PAYSTACK_SECRET_KEY = os.getenv('test_secret_paystack')