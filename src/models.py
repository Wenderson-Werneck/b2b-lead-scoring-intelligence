from typing import Literal, List, Optional
from pydantic import BaseModel, Field

AccountStatus = Literal["ACTIVE_CLIENT", "INACTIVE_CHURN", "UNTOUCHED_PROSPECT"]
AccountTier = Literal["TIER_A", "TIER_B", "TIER_C", "TIER_D"]


class CompanyLead(BaseModel):
    tax_id: str = Field(..., description="Anonymized company registration or VAT ID")
    company_name: str
    country: str = "BRA"
    account_status: AccountStatus
    annual_revenue_usd: float = Field(0.0, ge=0)
    historical_orders_count: int = Field(0, ge=0)
    consumed_hs_codes: List[str] = Field(default_factory=list)
    has_valid_contacts: bool = True
    shipping_distance_km: Optional[float] = None
    verified_trade_evidence: bool = False


class ScoredLead(BaseModel):
    tax_id: str
    company_name: str
    account_status: AccountStatus
    lead_score: int
    tier: AccountTier
    recommended_cross_sell_products: List[str]
    scoring_breakdown: dict
