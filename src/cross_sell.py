from typing import List, Dict, Set


class CrossSellRecommender:
    """
    Market basket and industrial metallurgy cross-selling matrix.
    Suggests complementary industrial raw materials based on active consumption.
    """

    # Knowledge graph of industrial affinities
    COMPLEMENTARY_MAP: Dict[str, List[str]] = {
        # Ferro-Silicon buyers frequently consume Inoculants, Nodulizers, and Calcium Silicon
        "720221": ["Calcium Silicon (CaSi)", "FeSi Nodulizers", "Recarburizer Carbon"],
        # Ferro-Manganese buyers frequently consume Low Carbon FeMn and Silicon Manganese
        "720211": ["Silicon-Manganese (SiMn)", "Medium Carbon FeMn", "Electrolytic Manganese Flakes"],
        # Ferro-Molybdenum buyers frequently consume Ferro-Vanadium and Ferro-Titanium
        "720270": ["Ferro-Vanadium (FeV)", "Ferro-Titanium (FeTi)", "Ferro-Niobium (FeNb)"],
        # Copper Cathodes / Non-ferrous
        "740311": ["Zinc Ingots", "Nickel Briquettes", "Tin Metal"],
    }

    @classmethod
    def recommend(cls, hs_codes: List[str]) -> List[str]:
        recommendations: Set[str] = set()
        for code in hs_codes:
            if code in cls.COMPLEMENTARY_MAP:
                recommendations.update(cls.COMPLEMENTARY_MAP[code])
        return sorted(list(recommendations))
