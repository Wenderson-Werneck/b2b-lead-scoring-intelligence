import pytest
from src.models import CompanyLead
from src.scorer import LeadScoringEngine
from src.cross_sell import CrossSellRecommender


def test_lead_scoring_tier_a_active_client():
    lead = CompanyLead(
        tax_id="EE102938475",
        company_name="Nordic Heavy Foundry AS",
        account_status="ACTIVE_CLIENT",
        annual_revenue_usd=5_000_000.0,
        historical_orders_count=12,
        consumed_hs_codes=["720211", "720221"],
        has_valid_contacts=True,
        shipping_distance_km=180.0,
        verified_trade_evidence=True,
    )

    score, tier, breakdown = LeadScoringEngine.calculate_score(lead)

    assert score >= 65
    assert tier == "TIER_A"
    assert breakdown["status_points"] == 20.0
    assert breakdown["contact_points"] == 10.0
    assert breakdown["logistics_points"] == 10.0


def test_lead_scoring_untouched_prospect():
    lead = CompanyLead(
        tax_id="EE998877665",
        company_name="Tallinn Metalworks OÜ",
        account_status="UNTOUCHED_PROSPECT",
        annual_revenue_usd=50_000.0,
        historical_orders_count=0,
        consumed_hs_codes=[],
        has_valid_contacts=False,
        shipping_distance_km=1500.0,
        verified_trade_evidence=False,
    )

    score, tier, breakdown = LeadScoringEngine.calculate_score(lead)

    assert score < 45
    assert tier in ["TIER_C", "TIER_D"]
    assert breakdown["sales_points"] == 0.0
    assert breakdown["contact_points"] == 0.0


def test_cross_sell_recommender():
    # FeMo buyer (720270)
    recs = CrossSellRecommender.recommend(["720270"])
    assert "Ferro-Vanadium (FeV)" in recs
    assert "Ferro-Niobium (FeNb)" in recs

    # Non-existent code
    empty = CrossSellRecommender.recommend(["999999"])
    assert empty == []
