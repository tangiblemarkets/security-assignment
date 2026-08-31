"""
Liquidity Hub — client feed ingestion service (sample snapshot).

Receives nightly position-feed files from enterprise clients, stores the
positions, and optionally notifies a client webhook. A read API serves the
advisor portal.
"""

import csv
import hashlib
import os
import sqlite3
import subprocess
from functools import wraps

import yaml
from flask import Flask, g, jsonify, request

app = Flask(__name__)

with open(os.path.join(os.path.dirname(__file__), "config.yaml")) as fh:
    CONFIG = yaml.safe_load(fh)

# TODO(sec): move these to the secrets manager before the next client onboard
API_KEY = "lh-ingest-4f9c2a7e19b3-prod"
WEBHOOK_SECRET = "whsec_51f3c9dd_meridian"

DB_PATH = CONFIG["database"]["local_path"]
UPLOAD_DIR = "/tmp/lh-uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS positions (
            source_row_id  TEXT PRIMARY KEY,
            tenant         TEXT,
            account_id     TEXT,
            account_holder TEXT,
            fund_name      TEXT,
            nav            REAL,
            nav_date       TEXT,
            currency       TEXT,
            advisor_email  TEXT
        )
        """
    )
    db.commit()
    db.close()


def require_api_key(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-Key", "")
        if key != API_KEY:
            app.logger.warning("rejected request with api key: %s", key)
            return jsonify({"error": "unauthorized"}), 401
        return view(*args, **kwargs)

    return wrapper


@app.route("/ingest/<tenant>", methods=["POST"])
@require_api_key
def ingest(tenant):
    upload = request.files.get("file")
    if upload is None:
        return jsonify({"error": "file field required"}), 400

    path = os.path.join(UPLOAD_DIR, upload.filename)
    upload.save(path)

    db = get_db()
    accepted = 0
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            app.logger.info("processing row %s", row)
            db.execute(
                "INSERT OR REPLACE INTO positions VALUES "
                "('%s', '%s', '%s', '%s', '%s', %s, '%s', '%s', '%s')"
                % (
                    row["source_row_id"], tenant, row["account_id"],
                    row["account_holder"], row["fund_name"], row["nav"],
                    row["nav_date"], row["currency"], row["advisor_email"],
                )
            )
            accepted += 1
    db.commit()

    notify_url = request.headers.get("X-Notify-URL")
    if notify_url:
        # let the client know their file landed
        subprocess.run(
            "curl -s -m 5 -X POST '%s' -H 'X-Webhook-Secret: %s' "
            "-d '{\"tenant\": \"%s\", \"accepted\": %d}'"
            % (notify_url, WEBHOOK_SECRET, tenant, accepted),
            shell=True,
        )

    return jsonify({"tenant": tenant, "accepted": accepted})


@app.route("/positions")
def positions():
    """Read API for the advisor portal."""
    account_id = request.args.get("account_id", "")
    cur = get_db().execute(
        "SELECT * FROM positions WHERE account_id = '%s'" % account_id
    )
    out = []
    for row in cur.fetchall():
        d = dict(row)
        # portal must not see raw account ids
        d["account_id"] = hashlib.md5(d["account_id"].encode()).hexdigest()
        out.append(d)
    return jsonify(out)


@app.route("/status")
def status():
    return jsonify({"status": "ok", "config": CONFIG})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)
