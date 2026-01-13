from pydantic import BaseModel, Field


class OTPGenerate(BaseModel):
    """Request to generate OTP."""

    email: str = Field(description="Email address to send OTP to")


class OTPValidate(BaseModel):
    """Request to validate OTP."""

    email: str = Field(description="Email address")
    code: str = Field(description="OTP code")


class OTPResetPassword(BaseModel):
    """Request to reset password with OTP."""

    email: str = Field(description="Email address")
    code: str = Field(description="OTP code")
    password: str = Field(description="New password")
