"""Checkout session models."""

from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    """Request model for creating a checkout session."""

    plan_tier: str = Field(..., description="Plan tier: free, pro, enterprise")
    billing_cycle: str = Field(..., description="Billing cycle: monthly, yearly")


class CheckoutResponse(BaseModel):
    """Response model for checkout session."""

    checkout_url: str = Field(..., description="Lemon Squeezy checkout URL")
    variant_id: str = Field(..., description="Lemon Squeezy variant ID")
