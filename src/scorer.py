import math
from typing import Dict, Any, Tuple
from src.models import CompanyLead, AccountTier


class LeadScoringEngine:
    """
    Computes multi-attribute B2B Lead Fit (ICP) score normalized from 0 to 100.
    """

    @staticmethod
    def calculate_score(lead: CompanyLead) -> Tuple[int, AccountTier, Dict[str, float]]:
        # 1. Account status base points (0 to 20 pts)
        status_points = {
            "ACTIVE_CLIENT": 20.0,
            "INACTIVE_CHURN": 14.0,
            "UNTOUCHED_PROSPECT": 6.0,
        }.get(lead.account_status, 0.0)

        # 2. Historical sales velocity (0 to 15 pts)
        sales_points = min(15.0, lead.historical_orders_count * 1.5)

        # 3. Log-scaled revenue points (0 to 15 pts)
        # Avoids distortion from mega-enterprises vs mid-market
        revenue_points = 0.0
        if lead.annual_revenue_usd > 1000:
            revenue_points = min(15.0, max(0.0, (math.log10(lead.annual_revenue_usd) - 3.0) * 3.0))

        # 4. Product / HS Code portfolio match (0 to 15 pts)
        hs_points = min(15.0, len(lead.consumed_hs_codes) * 5.0)

        # 5. Verified external trade evidence (Customs / DSI / NCM import records) (0 to 15 pts)
        evidence_points = 15.0 if lead.verified_trade_evidence else 0.0

        # 6. Contact availability (0 or 10 pts)
        contact_points = 10.0 if lead.has_valid_contacts else 0.0

        # 7. Logistics proximity bonus (0 to 10 pts)
        logistics_points = 0.0
        if lead.shipping_distance_km is not None and 0 < lead.shipping_distance_km <= 500:
            logistics_points = 10.0
        elif lead.shipping_distance_km is not None and lead.shipping_distance_km <= 1000:
            logistics_points = 5.0

        raw_total = (
            status_points
            + sales_points
            + revenue_points
            + hs_points
            + evidence_points
            + contact_points
            + logistics_points
        )

        final_score = min(100, max(0, round(raw_total)))

        # Tier assignment
        if final_score >= 65:
            tier: AccountTier = "TIER_A"
        elif final_score >= 45:
            tier = "TIER_B"
        elif final_score >= 25:
            tier = "TIER_C"
        else:
            tier = "TIER_D"

        breakdown = {
            "status_points": status_points,
            "sales_points": sales_points,
            "revenue_points": round(revenue_points, 2),
            "hs_points": hs_points,
            "evidence_points": evidence_points,
            "contact_points": contact_points,
            "logistics_points": logistics_points,
        }

        return final_score, tier, breakdown
