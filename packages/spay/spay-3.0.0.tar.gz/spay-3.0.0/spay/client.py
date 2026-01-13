import requests
from .configs import *


class SpayClient:
    def __init__(
        self,
        merchant_id: str,
        amount: int,
        callback_url: str = None,
        mobile: str = None,
        email: str = None,
        description: str = None,
    ):
        self.merchant_id = merchant_id
        self.amount = amount
        self.callback_url = callback_url
        self.mobile = mobile
        self.email = email
        self.description = description
        self.token = None
        self._token_url = TOKEN_URL
        self._request_payment = REQUEST_PAYMENT_URL
        self._verify_payment = VERIFY_PAYMENT_URL

    @staticmethod
    def _get_data(response, key_data: str) -> str:
        if response["code"] == 0:
            return response["data"][key_data]
        return response

    def _check_callback(self):
        if not self.callback_url:
            raise ValueError("callback_url is required for token generation")

    def get_token(self):
        """
        Requests a token from payment gateway.

        Returns:
             str: the token generated for the transaction.
        """

        self._check_callback()
        payload = {
            "amount": self.amount,
            "merchant_id": self.merchant_id,
            "callback_url": self.callback_url,
            "mobile": self.mobile,
            "email": self.email,
            "description": self.description,
        }

        self.token = self._get_data(
            requests.post(self._token_url, data=payload).json(), "token"
        )

        return self.token

    def request_payment(self):
        """
        Requests a payment from the payment gateway.

        Returns:
            str: the URL to proceed with the payment.
        """
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
        }

        return self._get_data(
            requests.get(self._request_payment, headers=headers).json(), "ipg_url"
        )

    def verify_payment(self, token: str):
        """
        Verifies the payment with the payment gateway.

        Args:
            token (str): the token to verify the payment.

        Returns:
            dict: the response from the payment gateway.
        """
        payload = {
            "merchant_id": self.merchant_id,
            "amount": self.amount,
            "token": token,
        }

        return requests.post(self._verify_payment, data=payload).json()
