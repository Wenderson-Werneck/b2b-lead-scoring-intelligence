# 🎯 B2B Industrial Lead Scoring & Market Intelligence Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Pydantic: v2](https://img.shields.io/badge/Pydantic-v2-green)](https://docs.pydantic.dev/)

A multi-attribute Ideal Customer Profile (ICP) lead scoring, tier classification (Tiers A/B/C/D), and industrial cross-selling recommendation engine designed for raw materials, bulk commodities, and manufacturing supply chains.

---

## 🏗 Scoring Framework & Mathematical Formulation

The engine computes an objective Lead Fit Score $S \in [0, 100]$ across 7 independent commercial and logistical dimensions:

$$S = \min\left(100, \; P_{\text{status}} + P_{\text{sales}} + P_{\text{revenue}} + P_{\text{portfolio}} + P_{\text{evidence}} + P_{\text{contact}} + P_{\text{logistics}}\right)$$

### Point Allocation Weights

| Dimension | Range | Criteria / Mathematical Model |
| :--- | :---: | :--- |
| **Account Status** ($P_{\text{status}}$) | 6 to 20 pts | Active client ($20$), Inactive churn ($14$), Untouched prospect ($6$). |
| **Sales Velocity** ($P_{\text{sales}}$) | 0 to 15 pts | $\min(15, \; \text{Historical Orders} \times 1.5)$. |
| **Log-Scaled Revenue** ($P_{\text{revenue}}$) | 0 to 15 pts | $\min(15, \; \max(0, \; (\log_{10}(\text{Revenue}) - 3) \times 3))$. Prevents skew from conglomerates. |
| **HS Code Affinity** ($P_{\text{portfolio}}$) | 0 to 15 pts | Product portfolio overlap based on 6-digit Harmonized System codes. |
| **Customs Evidence** ($P_{\text{evidence}}$) | 0 or 15 pts | Verified import/export filings (NCM/Siscomex/Bill of Lading records). |
| **Contact Data** ($P_{\text{contact}}$) | 0 or 10 pts | Verified buyer email, direct phone, or procurement desk. |
| **Logistics Proximity** ($P_{\text{logistics}}$) | 0 to 10 pts | Freight radius: $\le 500\text{ km} \rightarrow 10\text{ pts}$, $\le 1000\text{ km} \rightarrow 5\text{ pts}$. |

### Account Tiering

- **Tier A** ($S \ge 65$): High-priority immediate sales touch & executive engagement.
- **Tier B** ($45 \le S < 65$): Regular account management & cross-selling campaigns.
- **Tier C** ($25 \le S < 45$): Nurturing, automated newsletter & market monitoring.
- **Tier D** ($S < 25$): Disqualified or low-margin fit.

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/Wenderson-Werneck/b2b-lead-scoring-intelligence.git
cd b2b-lead-scoring-intelligence
pip install -r requirements.txt
```

### Running Test Suite

```bash
pytest -v
```

### Example Usage

```python
from src.scorer import LeadScoringEngine
from src.cross_sell import CrossSellRecommender
from src.models import CompanyLead

lead = CompanyLead(
    tax_id="EE102938475",
    company_name="Nordic Heavy Foundry AS",
    account_status="ACTIVE_CLIENT",
    annual_revenue_usd=8_500_000.0,
    historical_orders_count=14,
    consumed_hs_codes=["720211"],  # FeMn
    has_valid_contacts=True,
    shipping_distance_km=320.0,
    verified_trade_evidence=True,
)

score, tier, breakdown = LeadScoringEngine.calculate_score(lead)
cross_sell = CrossSellRecommender.recommend(lead.consumed_hs_codes)

print(f"Account: {lead.company_name} | Score: {score}/100 [{tier}]")
print(f"Recommended Cross-Sell: {cross_sell}")
```

---

## 🔒 Confidentiality & Data Protection

All sample entities, tax IDs, and commercial catalogs are strictly synthetic. No proprietary corporate customer lists or price agreements are contained in this repository.

## 📄 License

MIT © [Wenderson Werneck](https://github.com/Wenderson-Werneck)
