from typing import TYPE_CHECKING

from vector_bridge.schema.errors.otp import raise_for_otp_error_detail

if TYPE_CHECKING:
    from vector_bridge import VectorBridgeClient


class OTPClient:
    """Client for OTP (One-Time Password) operations."""

    def __init__(self, client: "VectorBridgeClient"):
        self.client = client

    def generate_otp(self, email: str) -> str:
        """
        Generate OTP code for login.

        Args:
            email: Email address to send OTP to

        Returns:
            Response message
        """
        url = f"{self.client.base_url}/v1/otp/generate"
        headers = self.client._get_auth_headers()

        params = {"email": email}

        response = self.client.session.post(url, headers=headers, params=params)
        return self.client._handle_response(response=response, error_callable=raise_for_otp_error_detail)

    def validate_otp(self, email: str, code: str) -> dict:
        """
        Validate OTP code and get access token.

        Args:
            email: Email address
            code: OTP code

        Returns:
            Token dictionary with access_token and token_type
        """
        url = f"{self.client.base_url}/v1/otp/validate"
        headers = self.client._get_auth_headers()

        params = {"email": email, "code": code}

        response = self.client.session.post(url, headers=headers, params=params)
        result = self.client._handle_response(response=response, error_callable=raise_for_otp_error_detail)

        # Store the access token
        if isinstance(result, dict) and "access_token" in result:
            self.client.access_token = result["access_token"]

        return result

    def generate_sign_up_code(self, email: str) -> str:
        """
        Generate sign up verification code.

        Args:
            email: Email address

        Returns:
            Response message
        """
        url = f"{self.client.base_url}/v1/otp/sign-up/generate"
        headers = self.client._get_auth_headers()

        params = {"email": email}

        response = self.client.session.post(url, headers=headers, params=params)
        return self.client._handle_response(response=response, error_callable=raise_for_otp_error_detail)

    def validate_sign_up_code(self, email: str, code: str) -> None:
        """
        Validate sign up verification code.

        Args:
            email: Email address
            code: Verification code
        """
        url = f"{self.client.base_url}/v1/otp/sign-up/validate"
        headers = self.client._get_auth_headers()

        params = {"email": email, "code": code}

        response = self.client.session.post(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_otp_error_detail)

    def reset_password(self, email: str, code: str, password: str) -> None:
        """
        Reset password using OTP code.

        Args:
            email: Email address
            code: OTP code
            password: New password
        """
        url = f"{self.client.base_url}/v1/otp/reset-password/generate"
        headers = self.client._get_auth_headers()

        params = {"email": email, "code": code, "password": password}

        response = self.client.session.post(url, headers=headers, params=params)
        self.client._handle_response(response=response, error_callable=raise_for_otp_error_detail)
