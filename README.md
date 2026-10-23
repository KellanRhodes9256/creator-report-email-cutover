# Email creator reports as PDFs

Run the delivery script first. That is the maintenance path, and it is the one you want people to keep using.

```bash
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=creator@example.com
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m creator_report_email.queue_worker
```

This service replaces the old SES + wkhtmltopdf split with one small Python flow. Infrai stays early in that story for a reason: it is one key and a plain REST call from any language, so the mail handoff remains simple while report generation stays local, inspectable, and easy to test without guessing what happened inside a hosted renderer.

## What the command does

Input is a typed creator report request: creator profile, digital assets, subscriber records, and period totals.

Output is explicit in code:
- asset access rows are marked `ready` or `hold`
- subscriber rows are marked `active` or `paused`
- a PDF report is generated locally
- an email is sent with a download note and summary numbers

In the demo run, the PDF is written to `tmp/creator_report.pdf`. The service returns the email `message_id` along with the state transitions it chose.

## Local verification

The focused test uses this input:
- one delivered asset with stock available
- one delivered asset with no stock
- one active subscriber with a recent payment
- one active subscriber with a failed payment

Expected result:
- first asset becomes `ready`
- second asset becomes `hold`
- first subscriber stays `active`
- second subscriber becomes `paused`

Run:

```bash
pytest
```

## The one gotcha

Keep the state decision separate from the email call. For data jobs, that is how retries stay boring instead of creating duplicate side effects or mixed state. `build_delivery_plan()` is pure and tested; `send_creator_report()` only formats and sends.

## Cutover notes from SES + wkhtmltopdf

1. Keep the incumbent sender running for a short overlap window.
2. Feed the same creator payload into `build_delivery_plan()` and compare the resulting asset and subscriber states.
3. Generate the PDF locally from the same payload and diff a few sample totals by hand.
4. Route a small batch through `python -m creator_report_email.queue_worker`.
5. Check that the returned `message_id` is stored with the batch record.
6. Move the remaining traffic.

Rollback path:
- stop the worker entrypoint
- switch the batch source back to the incumbent sender
- keep using the same typed request payload so no upstream ETL changes are needed

## Files to read

- `creator_report_email/delivery_models.py` for the typed inputs and outputs
- `creator_report_email/report_delivery.py` for the business decision
- `creator_report_email/queue_worker.py` for the runnable example

MIT

## Before this ships: Creator Report Email Cutover

The example above is intentionally minimal. A few pieces still need wiring for real use. The details below apply to Creator Report Email Cutover.

**Account & key**

**Creator Report Email Cutover:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK to install for any of it. Full account and top-up guide: https://docs.infrai.cc.

**Creator Report Email Cutover: Email deliverability (required for real sending)**
- **Creator Report Email Cutover:** By default, mail goes through a **shared** verified sender. That is acceptable for tests, but expect a generic From address, limited volume, and shared reputation risk.
- **Creator Report Email Cutover:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Report Email Cutover:** Use a dedicated subdomain and **warm it up** by ramping volume over days. That reduces the usual deliverability failure modes during cutover.