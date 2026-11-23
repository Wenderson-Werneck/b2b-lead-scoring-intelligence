"""
One-command interactive web demo for B2B Lead Scoring & Fiscal-Identity Portfolio Intelligence.
Run: python demo_app.py
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from src.models import CompanyLead
from src.scorer import LeadScoringEngine
from src.cross_sell import CrossSellRecommender
from src.portfolio_identity import build_fiscal_keyed_portfolio

PORT = int(os.environ.get("PORT", "8001"))

SYNTHETIC_LEADS = [
    CompanyLead(tax_id="EE-102.938-475", company_name="Nordic Heavy Foundry AS", account_status="ACTIVE_CLIENT", annual_revenue_usd=8_400_000, historical_orders_count=14, consumed_hs_codes=["720270", "720211"], has_valid_contacts=True, shipping_distance_km=160, verified_trade_evidence=True),
    CompanyLead(tax_id="ee102938475", company_name="Nordic Heavy Foundry (Legacy Alias)", account_status="ACTIVE_CLIENT", annual_revenue_usd=8_400_000, historical_orders_count=4, consumed_hs_codes=["720270"], has_valid_contacts=True, shipping_distance_km=160, verified_trade_evidence=True),
    CompanyLead(tax_id="FI-229.110-884", company_name="Baltic Alloy Works Oy", account_status="INACTIVE_CHURN", annual_revenue_usd=3_100_000, historical_orders_count=6, consumed_hs_codes=["720221"], has_valid_contacts=True, shipping_distance_km=420, verified_trade_evidence=True),
    CompanyLead(tax_id="SE-556.819-002", company_name="Scandia Steelworks AB", account_status="UNTOUCHED_PROSPECT", annual_revenue_usd=12_000_000, historical_orders_count=0, consumed_hs_codes=["720211", "720221"], has_valid_contacts=True, shipping_distance_km=680, verified_trade_evidence=True),
    CompanyLead(tax_id="LV-401.033-219", company_name="Riga Precision Castings SIA", account_status="UNTOUCHED_PROSPECT", annual_revenue_usd=480_000, historical_orders_count=0, consumed_hs_codes=[], has_valid_contacts=False, shipping_distance_km=1250, verified_trade_evidence=False),
]

SYNTHETIC_MOVEMENTS = [
    {"tax_id": "EE 102938475", "variant": "FeMo 65% Lump", "movement_type": "DIRECT_SALE", "metric_tons": 48.0},
    {"tax_id": "EE-102.938-475", "variant": "FeMn HC 78%", "movement_type": "DIRECT_SALE", "metric_tons": 120.5},
    {"tax_id": "FI-229.110-884", "variant": "FeSi 75% Fines", "movement_type": "CONSIGNMENT_RETURN", "metric_tons": 22.0},
]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>B2B Lead Scoring Intelligence — Live Demo</title>
  <style>
    :root { --bg:#0b1120; --card:#131c31; --surf:#0e1526; --bdr:#24324d; --txt:#f1f5f9; --mut:#94a3b8; --acc:#818cf8; --grn:#10b981; --amb:#f59e0b; --red:#ef4444; }
    * { box-sizing:border-box; font-family:-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",sans-serif; }
    body { margin:0; background:var(--bg); color:var(--txt); padding:24px; line-height:1.45; }
    .wrap { max-width:1280px; margin:0 auto; }
    header { display:flex; justify-content:space-between; align-items:center; padding-bottom:16px; margin-bottom:20px; border-bottom:1px solid var(--bdr); }
    h1 { margin:0; font-size:1.35rem; }
    .sub { margin:3px 0 0; font-size:0.84rem; color:var(--mut); }
    .pill { padding:5px 11px; border-radius:999px; font-size:0.75rem; font-weight:600; background:rgba(129,140,248,0.14); color:var(--acc); border:1px solid rgba(129,140,248,0.3); }
    .kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:18px; }
    .kpi { background:var(--card); border:1px solid var(--bdr); border-radius:10px; padding:14px 16px; }
    .kpi span { font-size:0.74rem; text-transform:uppercase; color:var(--mut); letter-spacing:0.04em; }
    .kpi strong { display:block; font-size:1.35rem; margin-top:5px; }
    .card { background:var(--card); border:1px solid var(--bdr); border-radius:10px; padding:18px; margin-bottom:18px; }
    .card h2 { margin:0 0 12px; font-size:0.88rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--mut); border-bottom:1px solid var(--bdr); padding-bottom:8px; }
    table { width:100%; border-collapse:collapse; font-size:0.84rem; font-variant-numeric:tabular-nums; }
    th, td { text-align:left; padding:9px 10px; border-bottom:1px solid var(--bdr); }
    th { font-size:0.73rem; text-transform:uppercase; color:var(--mut); }
    .badge { display:inline-block; padding:3px 8px; border-radius:4px; font-size:0.72rem; font-weight:700; }
    .TIER_A { background:rgba(16,185,129,0.16); color:var(--grn); }
    .TIER_B { background:rgba(129,140,248,0.16); color:var(--acc); }
    .TIER_C { background:rgba(245,158,11,0.16); color:var(--amb); }
    .TIER_D { background:rgba(239,68,68,0.16); color:var(--red); }
    .bar { height:7px; width:90px; background:var(--surf); border-radius:99px; overflow:hidden; display:inline-block; vertical-align:middle; margin-right:6px; }
    .bar i { display:block; height:100%; background:var(--acc); }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1>B2B Industrial ICP Lead Scoring &amp; Fiscal Portfolio Engine</h1>
        <p class="sub">7-Dimension ICP Scoring (0–100), Metallurgy Cross-Sell Matrix &amp; Canonical Fiscal-Identity Portfolio Deduplication</p>
      </div>
      <span class="pill">Python · Pydantic v2 · Synthetic B2B Data</span>
    </header>

    <div class="kpis" id="kpis"></div>

    <div class="card">
      <h2>Scored Industrial Accounts &amp; Cross-Sell Recommendations</h2>
      <table>
        <thead><tr><th>Company</th><th>Status</th><th>ICP Score</th><th>Tier</th><th>Revenue (USD)</th><th>Recommended Cross-Sell</th></tr></thead>
        <tbody id="leadsBody"></tbody>
      </table>
    </div>

    <div class="card">
      <h2>Canonical Fiscal-Identity Portfolio (Merged Aliases &amp; Variant Mix)</h2>
      <table>
        <thead><tr><th>Canonical Fiscal Key</th><th>Consolidated Name &amp; Aliases</th><th>Total Volume</th><th>Product Variant Mix</th><th>Movement Catalog</th></tr></thead>
        <tbody id="portBody"></tbody>
      </table>
    </div>
  </div>
  <script>
    fetch("/api/data").then(r => r.json()).then(d => {
      document.getElementById("kpis").innerHTML = `
        <div class="kpi"><span>Accounts Scored</span><strong>${d.scored.length}</strong></div>
        <div class="kpi"><span>Tier A Priority Accounts</span><strong style="color:var(--grn)">${d.scored.filter(x=>x.tier==="TIER_A").length}</strong></div>
        <div class="kpi"><span>Canonical Fiscal Entities</span><strong style="color:var(--acc)">${d.portfolio.length}</strong></div>
        <div class="kpi"><span>Duplicate Aliases Merged</span><strong>${d.scored.length - d.portfolio.length}</strong></div>
      `;
      document.getElementById("leadsBody").innerHTML = d.scored.map(l => `
        <tr>
          <td><strong>${l.company_name}</strong><br><small style="color:var(--mut)">${l.tax_id}</small></td>
          <td><code>${l.account_status}</code></td>
          <td><span class="bar"><i style="width:${l.score}%"></i></span><strong>${l.score}/100</strong></td>
          <td><span class="badge ${l.tier}">${l.tier}</span></td>
          <td>$${l.annual_revenue_usd.toLocaleString("en-US")}</td>
          <td>${l.cross_sell.length ? l.cross_sell.join(", ") : "<span style='color:var(--mut)'>Discovery required</span>"}</td>
        </tr>`).join("");
      document.getElementById("portBody").innerHTML = d.portfolio.map(p => `
        <tr>
          <td><code>${p.fiscal_key}</code></td>
          <td><strong>${p.canonical_name}</strong><br><small style="color:var(--mut)">Aliases: ${p.aliases.join(" · ")}</small></td>
          <td><strong>${p.total_tons.toFixed(1)} MT</strong></td>
          <td>${Object.entries(p.variant_mix_tons).map(([k,v]) => `${k}: ${v}t`).join(" | ") || "-"}</td>
          <td>${Object.entries(p.movement_catalog).map(([k,v]) => `${k} (${v})`).join(", ") || "-"}</td>
        </tr>`).join("");
    });
  </script>
</body>
</html>"""


class DemoHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))
        elif self.path == "/api/data":
            scored = []
            for lead in SYNTHETIC_LEADS:
                score, tier, breakdown = LeadScoringEngine.calculate_score(lead)
                scored.append({
                    "tax_id": lead.tax_id,
                    "company_name": lead.company_name,
                    "account_status": lead.account_status,
                    "annual_revenue_usd": lead.annual_revenue_usd,
                    "score": score,
                    "tier": tier,
                    "breakdown": breakdown,
                    "cross_sell": CrossSellRecommender.recommend(lead.consumed_hs_codes),
                })
            portfolio = list(build_fiscal_keyed_portfolio(SYNTHETIC_LEADS, SYNTHETIC_MOVEMENTS).values())
            payload = json.dumps({"scored": scored, "portfolio": portfolio}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    print(f"B2B Lead Scoring Intelligence Demo running at http://127.0.0.1:{PORT}")
    HTTPServer(("127.0.0.1", PORT), DemoHandler).serve_forever()
