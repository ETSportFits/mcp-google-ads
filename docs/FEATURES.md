# Google-Ads-MCP-Server — Feature- & Funktionsübersicht

## Was ist der Google-Ads-MCP-Server?

Der Google-Ads-MCP-Server ist eine Brücke zwischen **Google Ads** und KI-Assistenten wie **Claude** (Claude Desktop, Claude Code) oder **Cursor**. Er ist ein **MCP-Server** (Model Context Protocol) auf Basis von Python und **FastMCP**, der die Google-Ads-API als Sammlung klar abgegrenzter, KI-aufrufbarer Werkzeuge bereitstellt.

Konkret heißt das: Statt Reports manuell im Google-Ads-Interface zusammenzuklicken, GAQL-Abfragen von Hand zu bauen oder Performance-Daten in Tabellen zu exportieren, stellt man dem Assistenten einfach eine Frage in natürlicher Sprache — „Welche Kampagnen haben in den letzten 30 Tagen am besten performt?", „Zeig mir alle Anzeigentexte zur Account-ID X" oder „Welche Bild-Assets bringen die meisten Conversions?". Der Assistent ruft im Hintergrund das passende MCP-Tool auf, der Server holt die Daten live aus der Google-Ads-API, formatiert sie auf und gibt sie zurück. Der Assistent kann die Ergebnisse anschließend interpretieren, visualisieren und in Handlungsempfehlungen übersetzen.

**Kernnutzen auf einen Blick:**
- **Konversationelle Analyse** statt Klick-Marathon — Reporting in Alltagssprache.
- **Voller GAQL-Zugriff** — von vordefinierten Standardreports bis zur komplett freien Abfrage.
- **Multi-Account / MCC-fähig** — ein Login-Konto verwaltet beliebig viele Unterkonten.
- **Creative-Audit & Asset-Management** — Anzeigentexte, Bild-Assets, Asset-Nutzung und Asset-Performance auf Knopfdruck.
- **Flexible Authentifizierung** — OAuth 2.0 für Einzelnutzer, Service Account für Automatisierung.
- **Tooling-agnostisch** — funktioniert mit jedem MCP-Client (Claude Desktop, Claude Code, Cursor).

Der Server stellt aktuell **12 MCP-Tools** bereit (Google Ads API `v23`, stdio-Transport). Jedes Tool ist ein eigenständiges Feature und unten dokumentiert.

---

## Funktionsbereich 1 — Account- & Ressourcen-Discovery

Der Einstiegspunkt jeder Analyse: herausfinden, auf welche Konten man Zugriff hat und welche Datenobjekte abgefragt werden können.

### Feature: Konten auflisten (`list_accounts`)
- **Was es tut:** Listet alle Google-Ads-Konten auf, auf die die hinterlegten Zugangsdaten zugreifen können.
- **Wofür/Nutzen:** Der typische erste Befehl jeder Session — er liefert die Account-IDs, die in allen weiteren Tools gebraucht werden. Zielgruppe: jeder Nutzer, der mit mehreren Konten oder einem MCC-Setup arbeitet und nicht auswendig weiß, welche Customer-IDs verfügbar sind.
- **Parameter:** keine.
- **Liefert:** formatierte Liste aller zugänglichen Konten (Customer-IDs).
- **Wo:** Tool `list_accounts`, `google_ads_server.py`.

### Feature: Verfügbare GAQL-Ressourcen auflisten (`list_resources`)
- **Was es tut:** Listet alle gültigen Ressourcen auf, die in der `FROM`-Klausel einer GAQL-Abfrage verwendet werden dürfen (z. B. `campaign`, `ad_group`, `keyword_view`).
- **Wofür/Nutzen:** Verhindert fehlerhafte Abfragen, weil man sofort sieht, welche Datenobjekte überhaupt abfragbar sind. Zielgruppe: Power-User und Analysten, die eigene GAQL-Queries schreiben und das Schema der API-Version sicher kennen wollen.
- **Parameter:** `customer_id` (10-stellig, ohne Bindestriche).
- **Liefert:** formatierte Liste aller `RESOURCE`-Felder (intern via `google_ads_field`-Query über `run_gaql`).
- **Wo:** Tool `list_resources`, `google_ads_server.py`.

### Feature: Konto-Währung ermitteln (`get_account_currency`)
- **Was es tut:** Gibt den Standard-Währungscode des Kontos zurück (z. B. `EUR`, `USD`, `GBP`).
- **Wofür/Nutzen:** Pflicht-Schritt vor jeder Kostenanalyse — alle Kostenwerte der API kommen in „Micros" (Millionstel der Konto-Währung). Ohne den Währungscode lassen sich Cost-Werte nicht korrekt interpretieren. Zielgruppe: jeder, der Budgets, CPC, Kosten oder ROAS bewertet.
- **Parameter:** `customer_id`.
- **Liefert:** den Währungscode des Kontos.
- **Wo:** Tool `get_account_currency`, `google_ads_server.py`.

---

## Funktionsbereich 2 — Performance-Analyse & Reporting

Standardisierte, sofort einsetzbare Performance-Reports — ohne dass man selbst GAQL schreiben muss.

### Feature: Kampagnen-Performance (`get_campaign_performance`)
- **Was es tut:** Liefert die wichtigsten Performance-Kennzahlen je Kampagne für einen wählbaren Zeitraum (Impressionen, Klicks, Conversions, Kosten u. a.).
- **Wofür/Nutzen:** Das Brot-und-Butter-Reporting für Kampagnen-Manager — schnell sehen, welche Kampagnen liefern und welche Budget verbrennen. Ideal für wöchentliche/monatliche Reviews und Trend-Vergleiche. Zielgruppe: Performance-Marketer, Account-Manager, Geschäftsführung.
- **Parameter:** `customer_id`; `days` (Rückblick-Zeitraum, Default 30).
- **Liefert:** formatierte Tabelle der Kampagnen-Performance. Hinweis: Kostenwerte in Micros (1.000.000 = 1 Einheit der Konto-Währung).
- **Wo:** Tool `get_campaign_performance`, `google_ads_server.py`.

### Feature: Anzeigen-Performance (`get_ad_performance`)
- **Was es tut:** Liefert Performance-Kennzahlen auf Ebene einzelner Anzeigen für einen wählbaren Zeitraum.
- **Wofür/Nutzen:** Granularere Sicht als die Kampagnen-Ebene — zeigt, welche konkreten Anzeigen ziehen und welche unterperformen. Grundlage für A/B-Bewertung und das Pausieren schwacher Ads. Zielgruppe: Creative- und Performance-Teams.
- **Parameter:** `customer_id`; `days` (Default 30).
- **Liefert:** formatierte Tabelle der Anzeigen-Performance (Kostenwerte in Micros).
- **Wo:** Tool `get_ad_performance`, `google_ads_server.py`.

---

## Funktionsbereich 3 — Freie GAQL-Abfragen (Power-User)

Für alles, was über die Standardreports hinausgeht: direkter, unbegrenzter Zugriff auf die Google Ads Query Language.

### Feature: GAQL-Abfrage ausführen (`execute_gaql_query`)
- **Was es tut:** Führt eine beliebige, gültige GAQL-Abfrage gegen die Google-Ads-API aus und gibt das Ergebnis formatiert zurück.
- **Wofür/Nutzen:** Maximale Flexibilität für individuelle Auswertungen, die kein vordefiniertes Tool abdeckt — z. B. spezielle Segmentierungen, Keyword-Analysen oder Custom-Metriken. Zielgruppe: Analysten und Power-User mit GAQL-Kenntnissen.
- **Parameter:** `customer_id`; `query` (gültiger GAQL-String).
- **Liefert:** formatierte Query-Ergebnisse oder Fehlermeldung.
- **Wo:** Tool `execute_gaql_query`, `google_ads_server.py`.

### Feature: GAQL-Abfrage mit Formatwahl (`run_gaql`)
- **Was es tut:** Führt eine beliebige GAQL-Abfrage aus und gibt das Ergebnis im gewünschten Format zurück — **Tabelle**, **JSON** oder **CSV**.
- **Wofür/Nutzen:** Das mächtigste Tool des Servers. Die Format-Option macht es zur universellen Datenquelle: Tabelle für die schnelle Sichtung, JSON für Weiterverarbeitung durch den Assistenten, CSV für Export in Tabellenkalkulation/BI. Zielgruppe: Analysten, Daten-Teams, alle die GAQL-Ergebnisse weiterverarbeiten wollen. Mehrere Beispiel-Queries (Kampagnen-Metriken, Ad-Group-Performance, Keyword-Analyse) sind direkt im Tool dokumentiert.
- **Parameter:** `customer_id`; `query`; `format` (`table` | `json` | `csv`, Default `table`).
- **Liefert:** Query-Ergebnisse im gewählten Format.
- **Wo:** Tool `run_gaql`, `google_ads_server.py`.

---

## Funktionsbereich 4 — Creative- & Anzeigentext-Audit

Inhalte der Anzeigen sichtbar machen — für qualitative Bewertung statt reiner Zahlen.

### Feature: Anzeigen-Creatives abrufen (`get_ad_creatives`)
- **Was es tut:** Holt die tatsächlichen Anzeigeninhalte — Headlines, Descriptions und URLs — aus dem Konto.
- **Wofür/Nutzen:** Ermöglicht den qualitativen Creative-Audit: Texte auf Tonalität, Konsistenz, CTAs und Markenkonformität prüfen, ohne jede Anzeige einzeln im Interface zu öffnen. Der KI-Assistent kann die Texte direkt bewerten und Verbesserungen vorschlagen. Zielgruppe: Copywriter, Creative-Leads, Markenverantwortliche.
- **Parameter:** `customer_id`.
- **Liefert:** formatierte Liste der Anzeigen-Creatives (Headlines, Descriptions, URLs).
- **Wo:** Tool `get_ad_creatives`, `google_ads_server.py`.

---

## Funktionsbereich 5 — Bild-Asset-Management & Asset-Performance

Vollständiger Lebenszyklus für Bild-Assets: auflisten, herunterladen, Nutzung nachverfolgen, Performance bewerten.

### Feature: Bild-Assets auflisten (`get_image_assets`)
- **Was es tut:** Listet alle Bild-Assets des Kontos inklusive ihrer Voll-Auflösungs-Download-URLs auf.
- **Wofür/Nutzen:** Verschafft den Überblick über das vorhandene Bildmaterial und liefert die Asset-IDs/URLs für Weiterverarbeitung, Backup oder Analyse. Zielgruppe: Creative-Teams, Asset-Manager.
- **Parameter:** `customer_id`; `limit` (max. Anzahl Assets, Default 50).
- **Liefert:** formatierte Liste der Bild-Assets mit Download-URLs.
- **Wo:** Tool `get_image_assets`, `google_ads_server.py`.

### Feature: Bild-Asset herunterladen (`download_image_asset`)
- **Was es tut:** Lädt die Voll-Auflösungs-Version eines bestimmten Bild-Assets herunter und speichert sie lokal.
- **Wofür/Nutzen:** Für Backup, Archivierung oder externe Weiterverarbeitung (z. B. Re-Editing, Asset-Bibliothek). Zielgruppe: Creative-Ops, Designer, Archiv-Verantwortliche.
- **Parameter:** `customer_id`; `asset_id`; `output_dir` (Zielverzeichnis, Default `./ad_images`).
- **Liefert:** Status-Meldung über Erfolg/Misserfolg des Downloads.
- **Wo:** Tool `download_image_asset`, `google_ads_server.py`.

### Feature: Asset-Nutzung nachverfolgen (`get_asset_usage`)
- **Was es tut:** Findet, wo Assets im Konto eingesetzt werden — über Kampagnen, Anzeigengruppen und Anzeigen hinweg.
- **Wofür/Nutzen:** Beantwortet „Wo wird dieses Bild/dieser Text überhaupt verwendet?" — wichtig vor dem Löschen/Ersetzen von Assets und für die Creative-Optimierung. Funktioniert für mehrere Asset-Typen. Zielgruppe: Creative-Ops, Account-Manager.
- **Parameter:** `customer_id`; `asset_id` (optional — leer lassen für alle Assets des Typs); `asset_type` (`IMAGE` | `TEXT` | `VIDEO` u. a., Default `IMAGE`).
- **Liefert:** formatierter Report, wo die Assets im Konto verwendet werden.
- **Wo:** Tool `get_asset_usage`, `google_ads_server.py`.

### Feature: Bild-Asset-Performance analysieren (`analyze_image_assets`)
- **Was es tut:** Kombiniert Bild-Assets mit ihren Performance-Kennzahlen (Impressionen, Klicks, Conversions) über Kampagnen hinweg.
- **Wofür/Nutzen:** Die Antwort auf „Welche Bilder performen wirklich?" — datenbasierte Creative-Entscheidungen statt Bauchgefühl. Grundlage, um starke Visuals zu skalieren und schwache auszutauschen. Zielgruppe: Performance-Creative-Teams, Media-Buyer.
- **Parameter:** `customer_id`; `days` (Default 30).
- **Liefert:** detaillierter Report der Bild-Assets mit ihren Performance-Metriken.
- **Wo:** Tool `analyze_image_assets`, `google_ads_server.py`.

---

## Funktionsbereich 6 — Authentifizierung & Sicherheit (Querschnitt)

Kein einzelnes Tool, aber ein zentrales Feature des Servers: flexible, robuste Authentifizierung gegen die Google-Ads-API.

### Feature: Duale Authentifizierung (OAuth 2.0 & Service Account)
- **Was es tut:** Unterstützt zwei Auth-Methoden, umschaltbar per Konfiguration (`GOOGLE_ADS_AUTH_TYPE`): **OAuth 2.0** (Nutzer-Login, Default) und **Service Account** (Server-zu-Server, inkl. optionaler Domain-Wide-Delegation via Impersonation-E-Mail).
- **Wofür/Nutzen:** OAuth für Einzelnutzer und Desktop-Setups (interaktiver Login-Flow, lokaler Browser-Callback). Service Account für automatisierte/Server-Szenarien ohne menschliche Interaktion. Zielgruppe: vom Einzel-Marketer bis zum Engineering-Team mit Automatisierung.
- **Wo:** Funktionen `get_credentials`, `get_oauth_credentials`, `get_service_account_credentials`, `google_ads_server.py`.

### Feature: Automatischer Token-Refresh & -Persistenz
- **Was es tut:** Lädt gespeicherte OAuth-Tokens, erkennt abgelaufene Tokens und erneuert sie automatisch via Refresh-Token; speichert erneuerte Credentials zurück auf die Platte. Erkennt zudem, ob die Credential-Datei eine Client-Config oder ein bereits gespeichertes Token ist.
- **Wofür/Nutzen:** Der Nutzer muss sich nicht ständig neu anmelden — einmal eingerichtet, läuft die Auth im Hintergrund weiter. Robuste Fehlerbehandlung (`RefreshError`) startet bei Bedarf einen neuen Login-Flow. Zielgruppe: alle Nutzer (Komfort + Stabilität im Dauerbetrieb).
- **Wo:** `get_oauth_credentials`, `get_headers`, `google_ads_server.py`; Hilfsskript `reauth.py` (manuelle Re-Authentifizierung).

---

## Funktionsbereich 7 — MCC-/Multi-Account-Handling & Robustheit (Querschnitt)

### Feature: Manager-Account-(MCC-)Unterstützung
- **Was es tut:** Setzt bei gesetztem `GOOGLE_ADS_LOGIN_CUSTOMER_ID` automatisch den `login-customer-id`-Header, sodass über ein Manager-Konto (MCC) auf alle darunterliegenden Unterkonten zugegriffen werden kann.
- **Wofür/Nutzen:** Eine Anmeldung verwaltet beliebig viele Kundenkonten — essenziell für Agenturen und Unternehmen mit mehreren Ads-Konten. Zielgruppe: Agenturen, Multi-Brand-Unternehmen.
- **Wo:** `get_headers`, `google_ads_server.py`.

### Feature: Customer-ID-Normalisierung
- **Was es tut:** Bereinigt jede übergebene Customer-ID — entfernt Anführungszeichen, Bindestriche, Klammern und sonstige Nicht-Ziffern und füllt auf 10 Stellen auf.
- **Wofür/Nutzen:** Der Nutzer (oder der KI-Assistent) kann IDs in jedem gängigen Format liefern (`123-456-7890`, `"1234567890"`, `1234567890`) — der Server normalisiert sie zuverlässig. Verhindert eine häufige Fehlerquelle bei API-Aufrufen. Zielgruppe: alle Nutzer (Fehlervermeidung).
- **Wo:** `format_customer_id`, `google_ads_server.py`; Test `format_customer_id_test.py`.

---

## Funktionsbereich 8 — Konfiguration, Betrieb & Wissensbasis

### Feature: Umgebungsbasierte Konfiguration (`.env`)
- **Was es tut:** Alle Einstellungen werden über Umgebungsvariablen gesteuert: `GOOGLE_ADS_AUTH_TYPE`, `GOOGLE_ADS_CREDENTIALS_PATH`, `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_LOGIN_CUSTOMER_ID`, `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_IMPERSONATION_EMAIL`. Optional via `python-dotenv` aus einer `.env`-Datei geladen.
- **Wofür/Nutzen:** Saubere Trennung von Code und Secrets, einfache Einrichtung pro Umgebung. Eine `.env.example` dient als Vorlage. Zielgruppe: alle, die den Server installieren/betreiben.
- **Wo:** `.env.example`, Lade-Logik in `google_ads_server.py`.

### Feature: Installation & Betrieb (FastMCP, stdio)
- **Was es tut:** Python-Paket (`pyproject.toml` / `requirements.txt`, Python ≥ 3.11) mit FastMCP-Server, der über **stdio-Transport** läuft (`mcp.run(transport="stdio")`) und sich so in MCP-Clients wie Claude Desktop, Claude Code und Cursor einbinden lässt.
- **Wofür/Nutzen:** Standardisierte, client-agnostische Anbindung — einmal konfiguriert, in jedem MCP-fähigen Tool nutzbar. Zielgruppe: Engineering/Setup.
- **Wo:** `google_ads_server.py` (`__main__`-Block), `pyproject.toml`, `requirements.txt`, `README.md`.

### Feature: Integrierte GAQL-Wissensbasis & Tests
- **Was es tut:** Mitgelieferte Referenzdokumentation zu GAQL und FastMCP sowie eine Test-Suite.
- **Wofür/Nutzen:** Senkt die Einstiegshürde beim Schreiben eigener Queries (Syntax-Referenz + erprobte Beispiel-Queries) und sichert die Kernlogik ab (Token-Refresh, Customer-ID-Formatierung, End-to-End). Zielgruppe: Power-User (GAQL) und Entwickler (Qualitätssicherung).
- **Wo:** `docs/gaql-google-ads-query-language.md`, `docs/great-gaql-samples.md`, `docs/fastmcp.md`; Tests `test_google_ads_mcp.py`, `test_token_refresh.py`, `format_customer_id_test.py`.

---

## Selbst-Audit — Inventar-Abdeckung

**MCP-Tools (12):**
1. `list_accounts` ✅ (Bereich 1)
2. `list_resources` ✅ (Bereich 1)
3. `get_account_currency` ✅ (Bereich 1)
4. `get_campaign_performance` ✅ (Bereich 2)
5. `get_ad_performance` ✅ (Bereich 2)
6. `execute_gaql_query` ✅ (Bereich 3)
7. `run_gaql` ✅ (Bereich 3)
8. `get_ad_creatives` ✅ (Bereich 4)
9. `get_image_assets` ✅ (Bereich 5)
10. `download_image_asset` ✅ (Bereich 5)
11. `get_asset_usage` ✅ (Bereich 5)
12. `analyze_image_assets` ✅ (Bereich 5)

**Querschnitts-/Infrastruktur-Elemente (8):**
13. Duale Authentifizierung (OAuth + Service Account) ✅ (Bereich 6)
14. Automatischer Token-Refresh & -Persistenz (+ `reauth.py`) ✅ (Bereich 6)
15. MCC-/Manager-Account-Unterstützung ✅ (Bereich 7)
16. Customer-ID-Normalisierung ✅ (Bereich 7)
17. Umgebungsbasierte Konfiguration (`.env`) ✅ (Bereich 8)
18. Installation & Betrieb (FastMCP, stdio) ✅ (Bereich 8)
19. GAQL-/FastMCP-Wissensbasis ✅ (Bereich 8)
20. Test-Suite ✅ (Bereich 8)

**Abgedeckt: 20/20 Inventar-Elemente**
