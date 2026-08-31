# Feed ingestion service (sample snapshot)

Simplified snapshot of an internal Liquidity Hub service. It receives nightly
position-feed files from enterprise clients, stores the positions, optionally
notifies a client webhook, and serves a read API used by the advisor portal.

The contractor team that built it delivered it, got paid, and moved on. Treat
this as legacy code you inherited in week one.

## Components

- `app.py` — the Flask service (ingest + read API)
- `config.yaml` — service configuration
- `requirements.txt` — Python dependencies
- `terraform/main.tf` — AWS resources it runs against
- `.github/workflows/deploy.yml` — CI/CD that builds and deploys it

## API

| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /ingest/<tenant>` | `X-API-Key` header | Upload a positions CSV; optional `X-Notify-URL` header gets a callback with the accepted row count |
| `GET /positions?account_id=...` | — | Read API for the advisor portal (account IDs are hashed before returning) |
| `GET /status` | — | Health/status check |

## Intended behavior

- Each enterprise client drops one CSV per night; rows are keyed by
  `source_row_id`, re-deliveries overwrite.
- One shared ingest API key is currently used for all client tenants.
- The advisor portal calls `/positions` server-side and must never see raw
  account IDs.

## Running locally

```bash
pip install -r requirements.txt
python app.py   # serves on :8080
```

(You don't need to run it for the review — static review is fine.)
