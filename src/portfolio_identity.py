import re
from collections import defaultdict
from typing import Dict, List, Any
from src.models import CompanyLead


def canonicalize_fiscal_id(tax_id: str) -> str:
    """
    Normalizes corporate tax/VAT identifiers into a canonical fiscal key,
    preventing portfolio fragmentation caused by formatting or trade-name changes.
    """
    cleaned = re.sub(r"[^A-Za-z0-9]", "", (tax_id or "")).upper()
    if not cleaned:
        raise ValueError("INVALID_FISCAL_ID: Tax identifier cannot be empty.")
    return cleaned


def build_fiscal_keyed_portfolio(
    leads: List[CompanyLead],
    variant_movements: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Aggregates customer portfolios strictly by canonical fiscal identity, preserving
    trade-name aliases and detailing product variant mix across movement types.
    """
    portfolio: Dict[str, Dict[str, Any]] = {}

    for lead in leads:
        key = canonicalize_fiscal_id(lead.tax_id)
        if key not in portfolio:
            portfolio[key] = {
                "fiscal_key": key,
                "canonical_name": lead.company_name,
                "aliases": [lead.company_name],
                "account_status": lead.account_status,
                "variant_mix_tons": defaultdict(float),
                "movement_catalog": defaultdict(int),
                "total_tons": 0.0,
            }
        else:
            if lead.company_name not in portfolio[key]["aliases"]:
                portfolio[key]["aliases"].append(lead.company_name)

    for mv in variant_movements:
        key = canonicalize_fiscal_id(mv["tax_id"])
        if key not in portfolio:
            continue
        variant = str(mv.get("variant", "UNCLASSIFIED")).strip()
        movement_type = str(mv.get("movement_type", "STANDARD_SALE")).strip().upper()
        tons = float(mv.get("metric_tons", 0.0))

        portfolio[key]["variant_mix_tons"][variant] = round(
            portfolio[key]["variant_mix_tons"][variant] + tons, 3
        )
        portfolio[key]["movement_catalog"][movement_type] += 1
        portfolio[key]["total_tons"] = round(portfolio[key]["total_tons"] + tons, 3)

    # Convert defaultdicts to plain dicts for JSON serialization
    for entry in portfolio.values():
        entry["variant_mix_tons"] = dict(entry["variant_mix_tons"])
        entry["movement_catalog"] = dict(entry["movement_catalog"])

    return portfolio
