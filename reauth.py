#!/usr/bin/env python3
"""Re-authorise the Google Ads MCP by running a fresh OAuth consent flow.

Uses the client_id / client_secret that are already embedded in the existing
token file, so no manual secret handling is required. Writes a new token to
the same path the MCP server reads from.

Run:
    source .venv/bin/activate
    python reauth.py

Erstes Setup auf einem Rechner ohne Token-Datei: client_id und client_secret
des Desktop-OAuth-Clients kommen dann aus der Umgebung, und der Google-Account,
fuer den autorisiert wird, aus GOOGLE_ADS_LOGIN_HINT.

    GOOGLE_ADS_CLIENT_ID=... GOOGLE_ADS_CLIENT_SECRET=... \
    GOOGLE_ADS_LOGIN_HINT=vorname.nachname@sportfits.de python reauth.py
"""
import json
import os
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/adwords"]
TOKEN_PATH = os.environ.get(
    "GOOGLE_ADS_CREDENTIALS_PATH",
    os.path.expanduser("~/.config/google-ads-mcp/google_ads_token.json"),
)
LOGIN_HINT = os.environ.get("GOOGLE_ADS_LOGIN_HINT", "thorsten.eder@sportfits.de")


def main() -> int:
    # Ohne Token-Datei ist das ein Erstsetup: dann muessen die Client-Daten
    # aus der Umgebung kommen. Frueher brach das Skript hier ab, womit der
    # ENV-Fallback unten nie erreichbar war.
    old = {}
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH) as f:
            old = json.load(f)
    else:
        print(f"Keine Token-Datei unter {TOKEN_PATH} — Erstsetup aus der Umgebung.")

    client_id = old.get("client_id") or os.environ.get("GOOGLE_ADS_CLIENT_ID")
    client_secret = old.get("client_secret") or os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
    if not client_id or not client_secret:
        print(
            "client_id/client_secret fehlen. Entweder eine bestehende Token-Datei "
            "unter GOOGLE_ADS_CREDENTIALS_PATH, oder GOOGLE_ADS_CLIENT_ID und "
            "GOOGLE_ADS_CLIENT_SECRET setzen.",
            file=sys.stderr,
        )
        return 1

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    print(f"Opening browser for Google Ads re-auth (login_hint: {LOGIN_HINT})…")
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    # access_type=offline + prompt=consent → forces a fresh refresh_token
    creds = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
        login_hint=LOGIN_HINT,
    )

    # Verzeichnis und Datei von Anfang an eng: der Refresh-Token darf nie,
    # auch nicht kurz, mit Standardrechten auf der Platte liegen.
    os.makedirs(os.path.dirname(TOKEN_PATH), mode=0o700, exist_ok=True)
    fd = os.open(TOKEN_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(creds.to_json())
    # O_CREAT setzt den Modus nur bei Neuanlage — eine zu offene Altdatei nachziehen.
    os.chmod(TOKEN_PATH, 0o600)
    print(f"New token saved to {TOKEN_PATH}")
    print("Restart Claude Code (or reload the google-ads MCP) to pick it up.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
