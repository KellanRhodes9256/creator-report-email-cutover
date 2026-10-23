from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class CreatorProfile(BaseModel):
    creator_id: str
    creator_name: str
    email: EmailStr


class DigitalAssetDelivery(BaseModel):
    asset_id: str
    title: str
    delivered_units: int = Field(ge=0)
    remaining_stock: int = Field(ge=0)
    access_state: Literal["pending", "ready", "hold"] = "pending"


class SubscriberRecord(BaseModel):
    subscriber_id: str
    email: EmailStr
    last_payment_status: Literal["paid", "failed"]
    update_state: Literal["active", "paused"] = "active"


class ReportMetrics(BaseModel):
    gross_sales: Decimal
    net_payout: Decimal
    refunds: int = Field(ge=0)
    new_subscribers: int = Field(ge=0)


class CreatorReportRequest(BaseModel):
    report_id: str
    period_start: str
    period_end: str
    creator: CreatorProfile
    digital_assets: list[DigitalAssetDelivery]
    subscribers: list[SubscriberRecord]
    metrics: ReportMetrics


class DeliveryPlan(BaseModel):
    ready_asset_ids: list[str]
    hold_asset_ids: list[str]
    paused_subscriber_ids: list[str]
    pdf_path: str


class DeliveryResult(BaseModel):
    message_id: str
    plan: DeliveryPlan
