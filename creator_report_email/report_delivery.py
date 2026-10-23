from __future__ import annotations

from .delivery_models import CreatorReportRequest, DeliveryPlan, DeliveryResult
from .infrai_client import infrai
from .pdf_report import render_report_pdf


def build_delivery_plan(request: CreatorReportRequest, pdf_path: str) -> DeliveryPlan:
    ready_asset_ids: list[str] = []
    hold_asset_ids: list[str] = []
    paused_subscriber_ids: list[str] = []

    for asset in request.digital_assets:
        if asset.delivered_units <= asset.remaining_stock:
            asset.access_state = "ready"
            ready_asset_ids.append(asset.asset_id)
        else:
            asset.access_state = "hold"
            hold_asset_ids.append(asset.asset_id)

    for subscriber in request.subscribers:
        if subscriber.last_payment_status == "failed":
            subscriber.update_state = "paused"
            paused_subscriber_ids.append(subscriber.subscriber_id)
        else:
            subscriber.update_state = "active"

    final_pdf_path = render_report_pdf(request, pdf_path)
    return DeliveryPlan(
        ready_asset_ids=ready_asset_ids,
        hold_asset_ids=hold_asset_ids,
        paused_subscriber_ids=paused_subscriber_ids,
        pdf_path=final_pdf_path,
    )


def _build_email_html(request: CreatorReportRequest, plan: DeliveryPlan) -> str:
    return "".join(
        [
            f"<h1>{request.creator.creator_name} report</h1>",
            f"<p>Period: {request.period_start} to {request.period_end}</p>",
            f"<p>Gross sales: {request.metrics.gross_sales}</p>",
            f"<p>Net payout: {request.metrics.net_payout}</p>",
            f"<p>Assets ready: {len(plan.ready_asset_ids)}</p>",
            f"<p>Assets on hold: {len(plan.hold_asset_ids)}</p>",
            f"<p>Subscribers paused: {len(plan.paused_subscriber_ids)}</p>",
            f"<p>PDF saved at: {plan.pdf_path}</p>",
        ]
    )


def send_creator_report(request: CreatorReportRequest, pdf_path: str = "tmp/creator_report.pdf") -> DeliveryResult:
    plan = build_delivery_plan(request, pdf_path)
    payload = {
        "to": str(request.creator.email),
        "subject": f"Creator commerce report {request.period_end}",
        "html": _build_email_html(request, plan),
    }
    response = infrai.email.send(payload)
    message_id = response["data"]["message_id"]
    return DeliveryResult(message_id=message_id, plan=plan)
