from decimal import Decimal

from creator_report_email.delivery_models import (
    CreatorProfile,
    CreatorReportRequest,
    DigitalAssetDelivery,
    ReportMetrics,
    SubscriberRecord,
)
from creator_report_email.report_delivery import build_delivery_plan


def test_build_delivery_plan_marks_assets_and_subscribers(tmp_path):
    request = CreatorReportRequest(
        report_id="rpt_test",
        period_start="2026-03-01",
        period_end="2026-03-31",
        creator=CreatorProfile(
            creator_id="cr_test",
            creator_name="Pipeline Press",
            email="creator@example.com",
        ),
        digital_assets=[
            DigitalAssetDelivery(
                asset_id="asset_ready",
                title="Ready asset",
                delivered_units=1,
                remaining_stock=5,
            ),
            DigitalAssetDelivery(
                asset_id="asset_hold",
                title="Hold asset",
                delivered_units=4,
                remaining_stock=1,
            ),
        ],
        subscribers=[
            SubscriberRecord(
                subscriber_id="sub_active",
                email="active@example.com",
                last_payment_status="paid",
            ),
            SubscriberRecord(
                subscriber_id="sub_paused",
                email="paused@example.com",
                last_payment_status="failed",
            ),
        ],
        metrics=ReportMetrics(
            gross_sales=Decimal("100.00"),
            net_payout=Decimal("80.00"),
            refunds=0,
            new_subscribers=1,
        ),
    )

    plan = build_delivery_plan(request, str(tmp_path / "report.pdf"))

    assert plan.ready_asset_ids == ["asset_ready"]
    assert plan.hold_asset_ids == ["asset_hold"]
    assert plan.paused_subscriber_ids == ["sub_paused"]
    assert request.digital_assets[0].access_state == "ready"
    assert request.digital_assets[1].access_state == "hold"
    assert request.subscribers[0].update_state == "active"
    assert request.subscribers[1].update_state == "paused"
    assert tmp_path.joinpath("report.pdf").exists()
