from __future__ import annotations

from decimal import Decimal
import json
import os

from .delivery_models import (
    CreatorProfile,
    CreatorReportRequest,
    DigitalAssetDelivery,
    ReportMetrics,
    SubscriberRecord,
)
from .report_delivery import send_creator_report


def demo_request(email_to: str) -> CreatorReportRequest:
    return CreatorReportRequest(
        report_id="rpt_2026_03",
        period_start="2026-03-01",
        period_end="2026-03-31",
        creator=CreatorProfile(
            creator_id="cr_123",
            creator_name="Northwind Studio",
            email=email_to,
        ),
        digital_assets=[
            DigitalAssetDelivery(
                asset_id="asset_video_pack",
                title="Spring video pack",
                delivered_units=12,
                remaining_stock=20,
            ),
            DigitalAssetDelivery(
                asset_id="asset_licensing_bundle",
                title="Licensing bundle",
                delivered_units=8,
                remaining_stock=3,
            ),
        ],
        subscribers=[
            SubscriberRecord(
                subscriber_id="sub_001",
                email="paid@example.com",
                last_payment_status="paid",
            ),
            SubscriberRecord(
                subscriber_id="sub_002",
                email="failed@example.com",
                last_payment_status="failed",
            ),
        ],
        metrics=ReportMetrics(
            gross_sales=Decimal("1840.50"),
            net_payout=Decimal("1462.10"),
            refunds=2,
            new_subscribers=14,
        ),
    )


def main() -> None:
    email_to = os.environ["DEMO_EMAIL_TO"]
    request = demo_request(email_to)
    result = send_creator_report(request)
    print(
        json.dumps(
            {
                "message_id": result.message_id,
                "ready_asset_ids": result.plan.ready_asset_ids,
                "hold_asset_ids": result.plan.hold_asset_ids,
                "paused_subscriber_ids": result.plan.paused_subscriber_ids,
                "pdf_path": result.plan.pdf_path,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
