from __future__ import annotations

from pathlib import Path

from .delivery_models import CreatorReportRequest


def render_report_pdf(request: CreatorReportRequest, pdf_path: str) -> str:
    path = Path(pdf_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "%PDF-1.4",
        f"Creator report {request.report_id}",
        f"Creator: {request.creator.creator_name}",
        f"Period: {request.period_start} to {request.period_end}",
        f"Gross sales: {request.metrics.gross_sales}",
        f"Net payout: {request.metrics.net_payout}",
        f"Refunds: {request.metrics.refunds}",
        f"New subscribers: {request.metrics.new_subscribers}",
        "%%EOF",
    ]
    path.write_bytes("\n".join(lines).encode("utf-8"))
    return str(path)
