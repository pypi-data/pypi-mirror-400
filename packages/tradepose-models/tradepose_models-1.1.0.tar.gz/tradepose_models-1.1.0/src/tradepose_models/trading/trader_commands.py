"""Trader command models for Redis Stream communication (Issue #307, #320).

Pydantic models for trader commands published to Redis Streams:
- ExecuteOrderCommand: Open a new position
- CancelOrderCommand: Cancel an existing order
- ModifyOrderCommand: Modify SL/TP on existing order
- SyncBrokerStatusCommand: Request broker status sync

Stream pattern: trader:commands:{user_id}:{node_seq}:{slot_idx}
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from tradepose_models.enums import TradeDirection


class BaseTraderCommand(BaseModel):
    """Base class for all trader commands."""

    timestamp: datetime = Field(
        ...,
        description="Command creation timestamp (UTC)",
    )


class ExecuteOrderCommand(BaseTraderCommand):
    """Command to execute a new order.

    Published when an engagement is created and ready for execution.
    Contains all information needed to place entry order with SL/TP.
    """

    command_type: Literal["execute_order"] = Field(
        default="execute_order",
        description="Command type identifier",
    )
    engagement_id: UUID = Field(
        ...,
        description="Engagement UUID for tracking",
    )
    account_id: UUID = Field(
        ...,
        description="Trading account UUID",
    )
    symbol: str = Field(
        ...,
        description="Trading symbol (e.g., XAUUSD, MNQ)",
    )
    direction: TradeDirection = Field(
        ...,
        description="Trade direction: Long or Short",
    )
    quantity: Decimal = Field(
        ...,
        gt=0,
        description="Order quantity (lots)",
    )
    entry_price: Decimal = Field(
        ...,
        gt=0,
        description="Target entry price",
    )
    sl_price: Optional[Decimal] = Field(
        None,
        description="Stop loss price (optional)",
    )
    tp_price: Optional[Decimal] = Field(
        None,
        description="Take profit price (optional)",
    )


class CancelOrderCommand(BaseTraderCommand):
    """Command to cancel an existing order."""

    command_type: Literal["cancel_order"] = Field(
        default="cancel_order",
        description="Command type identifier",
    )
    engagement_id: UUID = Field(
        ...,
        description="Engagement UUID for tracking",
    )
    account_id: UUID = Field(
        ...,
        description="Trading account UUID",
    )
    broker_order_id: Optional[str] = Field(
        None,
        description="Broker's order ID to cancel (if known)",
    )


class ModifyOrderCommand(BaseTraderCommand):
    """Command to modify an existing order's SL/TP."""

    command_type: Literal["modify_order"] = Field(
        default="modify_order",
        description="Command type identifier",
    )
    engagement_id: UUID = Field(
        ...,
        description="Engagement UUID for tracking",
    )
    account_id: UUID = Field(
        ...,
        description="Trading account UUID",
    )
    broker_order_id: str = Field(
        ...,
        description="Broker's order ID to modify",
    )
    new_sl_price: Optional[Decimal] = Field(
        None,
        description="New stop loss price",
    )
    new_tp_price: Optional[Decimal] = Field(
        None,
        description="New take profit price",
    )


class SyncBrokerStatusCommand(BaseTraderCommand):
    """Command to request broker status synchronization."""

    command_type: Literal["sync_broker_status"] = Field(
        default="sync_broker_status",
        description="Command type identifier",
    )
    account_id: UUID = Field(
        ...,
        description="Trading account UUID to sync",
    )
