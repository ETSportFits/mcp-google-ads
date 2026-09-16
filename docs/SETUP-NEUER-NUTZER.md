# Google-Ads-MCP auf einem zweiten Rechner einrichten

Gilt für jede Person im Team, die Google-Ads-Daten in Claude Code lesen soll.
Der langsame Weg wäre ein eigener Developer-Token bei Google — den braucht
niemand. Der Developer-Token gehört dem Konto, nicht der Person.

Drei Dinge müssen zusammenkommen. Nur das erste dauert.

## 1. Zugang zum Google-Ads-Konto (das eigentliche Nadelöhr)

Ein Admin lädt die Person in `ads.google.com` → Verwaltung → Zugriff und
Sicherheit auf Kundenkonto **479-521-6660** ein. **Nur Lesezugriff**, außer es
gibt einen Grund für mehr. Die Einladung geht per Mail und muss angenommen
werden — ohne das liefert OAuth nachher ein leeres Konto zurück, kein Fehler.

Prüfen lässt sich der Stand hinterher so:

```
SELECT customer_user_access.email_address, customer_user_access.access_role
FROM customer_user_access
```

## 2. Repo und venv

```bash
git clone https://github.com/ETSportFits/mcp-google-ads.git ~/Repos/tools/mcp-google-ads
cd ~/Repos/tools/mcp-google-ads
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

## 3. Eigener OAuth-Token

Jede Person autorisiert sich selbst. Denselben Desktop-OAuth-Client benutzen
alle — `client_id` und `client_secret` kommen aus dem GCP-Projekt und dürfen
geteilt werden. Der **Refresh-Token** dagegen ist persönlich und wandert nie
zwischen Rechnern.

```bash
cd ~/Repos/tools/mcp-google-ads
GOOGLE_ADS_CLIENT_ID='<client_id>' \
GOOGLE_ADS_CLIENT_SECRET='<client_secret>' \
GOOGLE_ADS_LOGIN_HINT='vorname.nachname@sportfits.de' \
.venv/bin/python reauth.py
```

Der Browser geht auf, man meldet sich mit der Firmenadresse an, fertig. Der
Token landet mit Rechten 0600 unter `~/.config/google-ads-mcp/google_ads_token.json`.

## 4. MCP eintragen

In `~/.claude.json` unter `mcpServers`:

```json
"google-ads": {
  "type": "stdio",
  "command": "<HOME>/Repos/tools/mcp-google-ads/.venv/bin/python",
  "args": ["<HOME>/Repos/tools/mcp-google-ads/google_ads_server.py"],
  "env": {
    "GOOGLE_ADS_AUTH_TYPE": "oauth",
    "GOOGLE_ADS_CREDENTIALS_PATH": "<HOME>/.config/google-ads-mcp/google_ads_token.json",
    "GOOGLE_ADS_DEVELOPER_TOKEN": "<developer-token>"
  }
}
```

Claude Code neu starten, dann `list_accounts` aufrufen. Kommt die Kontoliste,
steht das Setup.

## Wenn es klemmt

Ein `404` auf der API heißt: die Versionsnummer in `google_ads_server.py` ist
abgeschaltet. Ein `401` heißt Auth. Der Unterschied ist der schnellste Test:

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://googleads.googleapis.com/v25/customers:listAccessibleCustomers
```

Der MCP liest nur. Mutationen laufen über REST, siehe `pmax-feed-only/feed_only.py`
in `sportfits-scripts`.
