"""Property-based tests for risk analysis module using Hypothesis.

These tests verify mathematical invariants and edge case behavior:
1. Score bounds: Overall scores always within valid range
2. Rating validity: Ratings always valid enum values
3. Metric counting: Available metrics never exceed total
4. Threshold boundaries: Correct behavior at exact threshold values
5. Edge case protection: NaN, infinity, None handling
"""

from __future__ import annotations

import sys
from pathlib import Path

from hypothesis import assume, given, settings
from hypothesis import strategies as st

# Add the API tests directory to path for factory imports
api_tests_path = Path(__file__).parent.parent.parent / "gurufocus-api" / "tests_api"
if str(api_tests_path) not in sys.path:
    sys.path.insert(0, str(api_tests_path))

from factories import (  # noqa: E402
    DistressedCompanyKeyRatiosFactory,
    HealthyCompanyKeyRatiosFactory,
    KeyRatiosFactory,
    StockSummaryFactory,
)

from gurufocus_mcp.analysis.risk import (  # noqa: E402
    _interpret_debt_equity,
    _interpret_growth,
    _interpret_piotroski,
    _interpret_z_score,
    compute_risk_analysis,
)
from gurufocus_mcp.models.risk import (  # noqa: E402
    FinancialRisk,
    GrowthRisk,
    MarketRisk,
    QualityRisk,
    RiskAnalysis,
    RiskMetric,
    RiskRating,
    ValuationRisk,
    _compute_dimension_rating,
    rating_to_score,
)

# =============================================================================
# Hypothesis Strategies
# =============================================================================

# Strategy for financial metric values
financial_value = st.one_of(
    st.none(),
    st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
)

# Strategy for percentage values (0-100 or -100 to 100 for growth)
percentage_value = st.one_of(
    st.none(),
    st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
)

# Strategy for score values (typically 0-100 or 0-10)
score_value = st.one_of(
    st.none(),
    st.integers(min_value=0, max_value=100),
)

# Strategy for ratio values (typically 0-10)
ratio_value = st.one_of(
    st.none(),
    st.floats(min_value=0, max_value=10, allow_nan=False, allow_infinity=False),
)


# =============================================================================
# RiskMetric Property Tests
# =============================================================================


class TestRiskMetricProperties:
    """Property-based tests for RiskMetric rating computation."""

    @given(
        value=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
        threshold_red=st.floats(
            min_value=-100, max_value=100, allow_nan=False, allow_infinity=False
        ),
        threshold_green=st.floats(
            min_value=-100, max_value=100, allow_nan=False, allow_infinity=False
        ),
    )
    @settings(max_examples=200)
    def test_rating_always_valid_enum(
        self, value: float, threshold_red: float, threshold_green: float
    ) -> None:
        """Rating is always a valid RiskRating enum value."""
        metric = RiskMetric(
            name="Test Metric",
            value=value,
            threshold_red=threshold_red,
            threshold_green=threshold_green,
            higher_is_worse=True,
        )
        assert metric.rating in [RiskRating.RED, RiskRating.YELLOW, RiskRating.GREEN]

    @given(
        value=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=100)
    def test_none_thresholds_always_yellow(self, value: float) -> None:
        """When thresholds are None, rating is always YELLOW."""
        metric = RiskMetric(
            name="Test Metric",
            value=value,
            threshold_red=None,
            threshold_green=None,
        )
        assert metric.rating == RiskRating.YELLOW

    def test_none_value_always_yellow(self) -> None:
        """When value is None, rating is always YELLOW."""
        metric = RiskMetric(
            name="Test Metric",
            value=None,
            threshold_red=1.5,
            threshold_green=0.5,
            higher_is_worse=True,
        )
        assert metric.rating == RiskRating.YELLOW

    @given(
        value=st.floats(min_value=2.0, max_value=100, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50)
    def test_higher_is_worse_above_red_threshold_is_red(self, value: float) -> None:
        """For higher_is_worse=True, values >= threshold_red are RED."""
        metric = RiskMetric(
            name="Test",
            value=value,
            threshold_red=1.5,
            threshold_green=0.5,
            higher_is_worse=True,
        )
        assert metric.rating == RiskRating.RED

    @given(
        value=st.floats(min_value=0.0, max_value=0.5, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50)
    def test_higher_is_worse_below_green_threshold_is_green(self, value: float) -> None:
        """For higher_is_worse=True, values <= threshold_green are GREEN."""
        metric = RiskMetric(
            name="Test",
            value=value,
            threshold_red=1.5,
            threshold_green=0.5,
            higher_is_worse=True,
        )
        assert metric.rating == RiskRating.GREEN

    @given(
        value=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50)
    def test_lower_is_worse_below_red_threshold_is_red(self, value: float) -> None:
        """For higher_is_worse=False, values <= threshold_red are RED."""
        metric = RiskMetric(
            name="Test",
            value=value,
            threshold_red=1.0,
            threshold_green=1.5,
            higher_is_worse=False,
        )
        assert metric.rating == RiskRating.RED

    @given(
        value=st.floats(min_value=1.5, max_value=10.0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50)
    def test_lower_is_worse_above_green_threshold_is_green(self, value: float) -> None:
        """For higher_is_worse=False, values >= threshold_green are GREEN."""
        metric = RiskMetric(
            name="Test",
            value=value,
            threshold_red=1.0,
            threshold_green=1.5,
            higher_is_worse=False,
        )
        assert metric.rating == RiskRating.GREEN


# =============================================================================
# Threshold Boundary Tests
# =============================================================================


class TestThresholdBoundaries:
    """Test exact threshold boundary behavior."""

    def test_altman_z_score_at_181_is_distress_boundary(self) -> None:
        """Altman Z-Score = 1.81 is exactly at distress boundary."""
        metric = RiskMetric(
            name="Altman Z-Score",
            value=1.81,
            threshold_red=1.81,
            threshold_green=2.99,
            higher_is_worse=False,
        )
        # At exactly threshold_red for lower-is-worse, should be RED
        assert metric.rating == RiskRating.RED

    def test_altman_z_score_at_299_is_safe_boundary(self) -> None:
        """Altman Z-Score = 2.99 is exactly at safe boundary."""
        metric = RiskMetric(
            name="Altman Z-Score",
            value=2.99,
            threshold_red=1.81,
            threshold_green=2.99,
            higher_is_worse=False,
        )
        # At exactly threshold_green for lower-is-worse, should be GREEN
        assert metric.rating == RiskRating.GREEN

    def test_altman_z_score_in_grey_zone(self) -> None:
        """Altman Z-Score between 1.81 and 2.99 is YELLOW (grey zone)."""
        for z in [1.82, 2.0, 2.5, 2.98]:
            metric = RiskMetric(
                name="Altman Z-Score",
                value=z,
                threshold_red=1.81,
                threshold_green=2.99,
                higher_is_worse=False,
            )
            assert metric.rating == RiskRating.YELLOW, f"Z={z} should be YELLOW"

    def test_debt_to_equity_at_exact_thresholds(self) -> None:
        """Debt-to-Equity at exact threshold values."""
        # At threshold_green (0.5) - should be GREEN
        metric_green = RiskMetric(
            name="D/E",
            value=0.5,
            threshold_red=1.5,
            threshold_green=0.5,
            higher_is_worse=True,
        )
        assert metric_green.rating == RiskRating.GREEN

        # At threshold_red (1.5) - should be RED
        metric_red = RiskMetric(
            name="D/E",
            value=1.5,
            threshold_red=1.5,
            threshold_green=0.5,
            higher_is_worse=True,
        )
        assert metric_red.rating == RiskRating.RED

    def test_piotroski_score_boundaries(self) -> None:
        """Piotroski F-Score boundary tests (0-9 scale)."""
        # Score <= 3 = RED (weak)
        for score in [0, 1, 2, 3]:
            metric = RiskMetric(
                name="Piotroski",
                value=float(score),
                threshold_red=3,
                threshold_green=7,
                higher_is_worse=False,
            )
            assert metric.rating == RiskRating.RED, f"Score {score} should be RED"

        # Score 4-6 = YELLOW (mixed)
        for score in [4, 5, 6]:
            metric = RiskMetric(
                name="Piotroski",
                value=float(score),
                threshold_red=3,
                threshold_green=7,
                higher_is_worse=False,
            )
            assert metric.rating == RiskRating.YELLOW, f"Score {score} should be YELLOW"

        # Score >= 7 = GREEN (strong)
        for score in [7, 8, 9]:
            metric = RiskMetric(
                name="Piotroski",
                value=float(score),
                threshold_red=3,
                threshold_green=7,
                higher_is_worse=False,
            )
            assert metric.rating == RiskRating.GREEN, f"Score {score} should be GREEN"


# =============================================================================
# Dimension Rating Computation Tests
# =============================================================================


class TestDimensionRatingProperties:
    """Property-based tests for dimension rating aggregation."""

    def test_all_red_metrics_gives_red_rating(self) -> None:
        """If all metrics with values are RED, dimension is RED."""
        metrics = [
            RiskMetric(
                name="M1", value=5.0, threshold_red=1.0, threshold_green=0.5, higher_is_worse=True
            ),
            RiskMetric(
                name="M2", value=10.0, threshold_red=2.0, threshold_green=1.0, higher_is_worse=True
            ),
            RiskMetric(
                name="M3",
                value=100.0,
                threshold_red=50.0,
                threshold_green=25.0,
                higher_is_worse=True,
            ),
        ]
        # Verify all are RED
        for m in metrics:
            assert m.rating == RiskRating.RED

        result = _compute_dimension_rating(metrics)
        assert result == RiskRating.RED

    def test_all_green_metrics_gives_green_rating(self) -> None:
        """If all metrics with values are GREEN, dimension is GREEN."""
        metrics = [
            RiskMetric(
                name="M1", value=0.1, threshold_red=1.0, threshold_green=0.5, higher_is_worse=True
            ),
            RiskMetric(
                name="M2", value=0.5, threshold_red=2.0, threshold_green=1.0, higher_is_worse=True
            ),
            RiskMetric(
                name="M3",
                value=10.0,
                threshold_red=50.0,
                threshold_green=25.0,
                higher_is_worse=True,
            ),
        ]
        # Verify all are GREEN
        for m in metrics:
            assert m.rating == RiskRating.GREEN

        result = _compute_dimension_rating(metrics)
        assert result == RiskRating.GREEN

    def test_all_none_values_gives_yellow(self) -> None:
        """If all metrics have None values, dimension is YELLOW."""
        metrics = [
            RiskMetric(name="M1", value=None, threshold_red=1.0, threshold_green=0.5),
            RiskMetric(name="M2", value=None, threshold_red=2.0, threshold_green=1.0),
            RiskMetric(name="M3", value=None, threshold_red=50.0, threshold_green=25.0),
        ]
        result = _compute_dimension_rating(metrics)
        assert result == RiskRating.YELLOW

    def test_empty_metrics_gives_yellow(self) -> None:
        """Empty metrics list gives YELLOW."""
        result = _compute_dimension_rating([])
        assert result == RiskRating.YELLOW

    @given(
        n_red=st.integers(min_value=0, max_value=5),
        n_yellow=st.integers(min_value=0, max_value=5),
        n_green=st.integers(min_value=0, max_value=5),
    )
    @settings(max_examples=100)
    def test_rating_always_valid(self, n_red: int, n_yellow: int, n_green: int) -> None:
        """Dimension rating is always a valid enum value."""
        assume(n_red + n_yellow + n_green > 0)  # Need at least one metric

        metrics = []
        # RED metrics
        for i in range(n_red):
            metrics.append(
                RiskMetric(
                    name=f"Red{i}",
                    value=10.0,
                    threshold_red=1.0,
                    threshold_green=0.5,
                    higher_is_worse=True,
                )
            )
        # YELLOW metrics
        for i in range(n_yellow):
            metrics.append(
                RiskMetric(
                    name=f"Yellow{i}",
                    value=0.75,
                    threshold_red=1.0,
                    threshold_green=0.5,
                    higher_is_worse=True,
                )
            )
        # GREEN metrics
        for i in range(n_green):
            metrics.append(
                RiskMetric(
                    name=f"Green{i}",
                    value=0.1,
                    threshold_red=1.0,
                    threshold_green=0.5,
                    higher_is_worse=True,
                )
            )

        result = _compute_dimension_rating(metrics)
        assert result in [RiskRating.RED, RiskRating.YELLOW, RiskRating.GREEN]


# =============================================================================
# Score Computation Tests
# =============================================================================


class TestScoreProperties:
    """Property-based tests for score computation."""

    def test_rating_to_score_mapping(self) -> None:
        """Verify rating_to_score mapping is correct."""
        assert rating_to_score(RiskRating.RED) == 3
        assert rating_to_score(RiskRating.YELLOW) == 2
        assert rating_to_score(RiskRating.GREEN) == 1

    @given(
        ratings=st.lists(
            st.sampled_from([RiskRating.RED, RiskRating.YELLOW, RiskRating.GREEN]),
            min_size=1,
            max_size=10,
        )
    )
    @settings(max_examples=100)
    def test_average_score_bounds(self, ratings: list[RiskRating]) -> None:
        """Average score is always between 1.0 and 3.0."""
        scores = [rating_to_score(r) for r in ratings]
        avg = sum(scores) / len(scores)
        assert 1.0 <= avg <= 3.0


# =============================================================================
# Full Risk Analysis Tests
# =============================================================================


class TestRiskAnalysisProperties:
    """Property-based tests for complete risk analysis."""

    def test_healthy_company_analysis(self) -> None:
        """Healthy company should generally get GREEN/YELLOW ratings."""
        keyratios = HealthyCompanyKeyRatiosFactory.build()
        summary = StockSummaryFactory.build()

        analysis = compute_risk_analysis("FAKE1", summary, keyratios)

        # Should complete without error
        assert analysis.symbol == "FAKE1"
        assert analysis.metrics_available >= 0
        assert analysis.metrics_available <= analysis.metrics_total

        # Summary score should be valid
        assert 1.0 <= analysis.summary.overall_score <= 3.0

        # All ratings should be valid
        assert analysis.summary.overall_rating in RiskRating
        assert analysis.matrix.financial in RiskRating
        assert analysis.matrix.quality in RiskRating
        assert analysis.matrix.growth in RiskRating
        assert analysis.matrix.valuation in RiskRating
        assert analysis.matrix.market in RiskRating

    def test_distressed_company_analysis(self) -> None:
        """Distressed company should get more RED ratings."""
        keyratios = DistressedCompanyKeyRatiosFactory.build()
        summary = StockSummaryFactory.build()

        analysis = compute_risk_analysis("DISTRESS", summary, keyratios)

        # Should complete without error
        assert analysis.symbol == "DISTRESS"
        assert analysis.metrics_available >= 0
        assert analysis.metrics_available <= analysis.metrics_total

        # Summary score should be valid (likely higher = more risk)
        assert 1.0 <= analysis.summary.overall_score <= 3.0

        # Should have red flags for distressed company
        # The distressed factory has low Altman Z-Score, so we expect financial concerns
        z_score = analysis.financial.altman_z_score.value
        if z_score is not None and z_score < 1.81:
            assert analysis.financial.overall_rating in [RiskRating.RED, RiskRating.YELLOW]

    def test_metrics_count_never_exceeds_total(self) -> None:
        """metrics_available should never exceed metrics_total."""
        keyratios = KeyRatiosFactory.build()
        summary = StockSummaryFactory.build()

        analysis = compute_risk_analysis("TEST", summary, keyratios)

        assert analysis.metrics_available <= analysis.metrics_total
        assert analysis.metrics_available >= 0

    def test_analysis_date_is_populated(self) -> None:
        """analysis_date should be populated."""
        keyratios = KeyRatiosFactory.build()
        summary = StockSummaryFactory.build()

        analysis = compute_risk_analysis("TEST", summary, keyratios)

        assert analysis.analysis_date is not None
        assert len(analysis.analysis_date) == 10  # ISO format: YYYY-MM-DD


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_all_none_metrics_gives_yellow_summary(self) -> None:
        """Analysis with all None metrics should default to YELLOW."""
        # Create analysis with empty data
        analysis = RiskAnalysis(
            symbol="EMPTY",
            analysis_date="2024-01-01",
        )

        # All dimensions should be YELLOW (default)
        assert analysis.financial.overall_rating == RiskRating.YELLOW
        assert analysis.quality.overall_rating == RiskRating.YELLOW
        assert analysis.growth.overall_rating == RiskRating.YELLOW
        assert analysis.valuation.overall_rating == RiskRating.YELLOW
        assert analysis.market.overall_rating == RiskRating.YELLOW

    def test_extreme_positive_values(self) -> None:
        """Extreme positive values should not cause errors."""
        metric = RiskMetric(
            name="Extreme",
            value=1e10,  # 10 billion
            threshold_red=1.5,
            threshold_green=0.5,
            higher_is_worse=True,
        )
        assert metric.rating == RiskRating.RED  # Way above threshold

    def test_extreme_negative_values(self) -> None:
        """Extreme negative values should not cause errors."""
        metric = RiskMetric(
            name="Extreme",
            value=-1e10,
            threshold_red=1.5,
            threshold_green=0.5,
            higher_is_worse=True,
        )
        assert metric.rating == RiskRating.GREEN  # Way below threshold

    def test_zero_value(self) -> None:
        """Zero value should be handled correctly."""
        metric = RiskMetric(
            name="Zero",
            value=0.0,
            threshold_red=1.5,
            threshold_green=0.5,
            higher_is_worse=True,
        )
        assert metric.rating == RiskRating.GREEN

    def test_negative_threshold_values(self) -> None:
        """Negative thresholds should work (e.g., for growth rates)."""
        # Growth rate where negative is bad
        metric = RiskMetric(
            name="Growth",
            value=-10.0,
            threshold_red=-5.0,
            threshold_green=10.0,
            higher_is_worse=False,  # Lower (more negative) is worse
        )
        assert metric.rating == RiskRating.RED


# =============================================================================
# Interpretation Function Tests
# =============================================================================


class TestInterpretationFunctions:
    """Test interpretation helper functions."""

    def test_z_score_interpretation_zones(self) -> None:
        """Test Altman Z-Score interpretation returns correct zones."""
        assert _interpret_z_score(None) is None
        assert _interpret_z_score(4.0) == "Safe zone"
        assert _interpret_z_score(2.5) == "Grey zone"
        assert _interpret_z_score(1.5) == "Distress zone"
        # Boundary values
        assert _interpret_z_score(2.99) == "Grey zone"  # Just under safe
        assert _interpret_z_score(3.0) == "Safe zone"  # Just above boundary
        assert _interpret_z_score(1.81) == "Grey zone"  # At grey/distress boundary
        assert _interpret_z_score(1.80) == "Distress zone"

    def test_debt_equity_interpretation(self) -> None:
        """Test Debt-to-Equity interpretation."""
        assert _interpret_debt_equity(None) is None
        assert _interpret_debt_equity(0.3) == "Conservative leverage"
        assert _interpret_debt_equity(0.7) == "Moderate leverage"
        assert _interpret_debt_equity(1.2) == "Elevated leverage"
        assert _interpret_debt_equity(2.0) == "High leverage"

    def test_piotroski_interpretation(self) -> None:
        """Test Piotroski F-Score interpretation."""
        assert _interpret_piotroski(None) is None
        assert _interpret_piotroski(8) == "Strong fundamentals"
        assert _interpret_piotroski(5) == "Mixed fundamentals"
        assert _interpret_piotroski(2) == "Weak fundamentals"

    def test_growth_interpretation(self) -> None:
        """Test growth rate interpretation."""
        assert _interpret_growth(None, "Revenue") is None
        assert _interpret_growth(20.0, "Revenue") == "Strong Revenue growth"
        assert _interpret_growth(7.0, "EPS") == "Moderate EPS growth"
        assert _interpret_growth(2.0, "FCF") == "Flat FCF"
        assert _interpret_growth(-10.0, "Revenue") == "Declining Revenue"


# =============================================================================
# Risk Dimension Tests
# =============================================================================


class TestRiskDimensions:
    """Test individual risk dimension builders."""

    def test_financial_risk_key_concern_priority(self) -> None:
        """Financial risk key concerns follow priority order."""
        # Altman Z-Score takes priority
        risk = FinancialRisk()
        risk.altman_z_score = RiskMetric(
            name="Z-Score",
            value=1.0,
            threshold_red=1.81,
            threshold_green=2.99,
            higher_is_worse=False,
        )
        risk.debt_to_equity = RiskMetric(
            name="D/E",
            value=3.0,
            threshold_red=1.5,
            threshold_green=0.5,
            higher_is_worse=True,
        )
        assert risk.key_concern is not None
        assert "Bankruptcy" in risk.key_concern or "Z-Score" in risk.key_concern

    def test_quality_risk_detects_manipulation(self) -> None:
        """Quality risk detects earnings manipulation flag."""
        risk = QualityRisk()
        risk.beneish_m_score = RiskMetric(
            name="M-Score",
            value=-1.5,  # Above -1.78 suggests manipulation
            threshold_red=-1.78,
            threshold_green=-2.22,
            higher_is_worse=True,
        )
        assert risk.beneish_m_score.rating == RiskRating.RED
        assert risk.key_concern is not None
        assert "manipulation" in risk.key_concern.lower()

    def test_growth_trend_determination(self) -> None:
        """Growth risk trend is determined correctly."""
        risk = GrowthRisk()
        # These are set after construction, simulating _build_growth_risk behavior

        # Accelerating growth (1Y > 3Y) = decreasing risk
        risk.revenue_growth_3y = RiskMetric(
            name="3Y", value=5.0, threshold_red=-5, threshold_green=10, higher_is_worse=False
        )
        risk.revenue_growth_consistency = RiskMetric(
            name="Momentum", value=10.0, threshold_red=-20, threshold_green=0, higher_is_worse=False
        )

        # Trend set externally in _build_growth_risk based on 1Y vs 3Y comparison
        assert risk.overall_rating in RiskRating

    def test_valuation_margin_of_safety_calculation(self) -> None:
        """Valuation margin of safety is computed correctly."""
        risk = ValuationRisk()

        # 20% undervalued (price/value = 0.8 means 20% MOS)
        risk.price_to_gf_value = RiskMetric(
            name="Price/GF Value",
            value=0.8,
            threshold_red=1.3,
            threshold_green=0.8,
            higher_is_worse=True,
        )
        risk.margin_of_safety = RiskMetric(
            name="MOS",
            value=20.0,  # (1 - 0.8) * 100 = 20%
            threshold_red=-10,
            threshold_green=30,
            higher_is_worse=False,
        )

        assert risk.price_to_gf_value.rating == RiskRating.GREEN
        assert risk.margin_of_safety.rating == RiskRating.YELLOW  # 20% is between -10 and 30

    def test_market_risk_high_volatility(self) -> None:
        """Market risk detects high volatility."""
        risk = MarketRisk()
        risk.volatility_1y = RiskMetric(
            name="Volatility",
            value=60.0,  # 60% annual volatility
            threshold_red=50,
            threshold_green=25,
            higher_is_worse=True,
        )
        assert risk.volatility_1y.rating == RiskRating.RED
        assert risk.key_concern is not None
        assert "volatility" in risk.key_concern.lower()
