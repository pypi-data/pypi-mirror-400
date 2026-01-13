from decimal import Decimal

import pytest

from osvc_kalkulacka.cli import load_year_defaults
from osvc_kalkulacka.core import Inputs, Section7Item, compute, compute_insurance


def test_compute_regression_2025_example():
    inp = Inputs(
        section_7_items=(Section7Item(income_czk=800_000, expense_rate=Decimal("0.60")),),
        child_months_by_order=(12,),
        min_wage_czk=20_800,
        section_15_allowances_czk=150_000,
        tax_rate=Decimal("0.15"),
        taxpayer_credit_czk=30_840,
        spouse_allowance_czk=24_840,
        child_bonus_annual_tiers_czk=(15_204, 22_320, 27_840),
        avg_wage_czk=46_557,
        zp_rate=Decimal("0.135"),
        sp_rate=Decimal("0.292"),
        zp_vym_base_share=Decimal("0.50"),
        sp_vym_base_share=Decimal("0.55"),
        zp_min_base_share=Decimal("0.50"),
        sp_min_base_share=Decimal("0.35"),
    )

    res = compute(inp)

    assert res.tax.base_profit_czk == 320_000
    assert res.tax.tax_final_czk == 0
    assert res.tax.bonus_to_pay_czk == 15_204
    assert res.ins.zp_annual_payable_czk == 37_712
    assert res.ins.sp_annual_payable_czk == 57_098
    assert res.ins.zp_annual_prescribed_czk == 37_716
    assert res.ins.sp_annual_prescribed_czk == 57_108


def test_child_bonus_ineligible_when_income_below_minimum():
    inp = Inputs(
        section_7_items=(Section7Item(income_czk=100_000, expense_rate=Decimal("0.60")),),
        child_months_by_order=(12,),
        min_wage_czk=20_800,
        section_15_allowances_czk=0,
        tax_rate=Decimal("0.15"),
        taxpayer_credit_czk=30_840,
        spouse_allowance_czk=0,
        child_bonus_annual_tiers_czk=(15_204, 22_320, 27_840),
        avg_wage_czk=0,
        zp_rate=Decimal("0.135"),
        sp_rate=Decimal("0.292"),
        zp_vym_base_share=Decimal("0.50"),
        sp_vym_base_share=Decimal("0.55"),
        zp_min_base_share=Decimal("0.0"),
        sp_min_base_share=Decimal("0.0"),
    )

    res = compute(inp)

    assert res.tax.child_bonus_eligible is False
    assert res.tax.child_bonus_czk == 0


def test_minimums_use_avg_wage_when_profit_low():
    inp = Inputs(
        child_months_by_order=(),
        min_wage_czk=0,
        section_15_allowances_czk=0,
        tax_rate=Decimal("0.15"),
        taxpayer_credit_czk=0,
        spouse_allowance_czk=0,
        child_bonus_annual_tiers_czk=(15_204, 22_320, 27_840),
        avg_wage_czk=100,
        zp_rate=Decimal("0.10"),
        sp_rate=Decimal("0.20"),
        zp_vym_base_share=Decimal("0.50"),
        sp_vym_base_share=Decimal("0.55"),
        zp_min_base_share=Decimal("0.50"),
        sp_min_base_share=Decimal("0.40"),
    )

    res = compute(inp)

    assert res.ins.min_zp_monthly_czk == 5
    assert res.ins.min_sp_monthly_czk == 8
    assert res.ins.zp_annual_payable_czk == 60
    assert res.ins.sp_annual_payable_czk == 96


def test_minimum_monthly_rounding_uses_ceiling():
    inp = Inputs(
        child_months_by_order=(),
        min_wage_czk=0,
        avg_wage_czk=101,
        zp_rate=Decimal("0.10"),
        sp_rate=Decimal("0.10"),
        zp_min_base_share=Decimal("0.50"),
        sp_min_base_share=Decimal("0.50"),
    )

    ins = compute_insurance(inp, 0)

    assert ins.min_zp_monthly_czk == 6
    assert ins.min_sp_monthly_czk == 6
    assert ins.zp_monthly_payable_czk == 6
    assert ins.sp_monthly_payable_czk == 6
    assert ins.zp_annual_payable_czk == 61
    assert ins.sp_annual_payable_czk == 61


def test_annual_prescribed_matches_monthly_times_12():
    inp = Inputs(
        child_months_by_order=(),
        min_wage_czk=0,
        avg_wage_czk=101,
        zp_rate=Decimal("0.10"),
        sp_rate=Decimal("0.10"),
        zp_min_base_share=Decimal("0.50"),
        sp_min_base_share=Decimal("0.50"),
    )

    ins = compute_insurance(inp, 0)

    assert ins.zp_annual_prescribed_czk == ins.zp_monthly_payable_czk * 12
    assert ins.sp_annual_prescribed_czk == ins.sp_monthly_payable_czk * 12


def test_minimums_match_official_values_2022_2026():
    year_defaults = load_year_defaults("osvc_kalkulacka/data/year_defaults.toml", user_dir=".")
    expected = {
        2022: (2627, 2841),
        2023: (2722, 2944),
        2024: (2968, 3852),
        2025: (3143, 4759),
        2026: (3306, 5720),
    }

    for year, (expected_zp, expected_sp) in expected.items():
        cfg = year_defaults[year]
        inp = Inputs(
            child_months_by_order=(),
            min_wage_czk=0,
            avg_wage_czk=cfg["avg_wage_czk"],
            sp_min_base_share=cfg["sp_min_base_share"],
            sp_vym_base_share=cfg["sp_vym_base_share"],
        )
        ins = compute_insurance(inp, 0)

        assert ins.min_zp_monthly_czk == expected_zp
        assert ins.min_sp_monthly_czk == expected_sp


def test_secondary_activity_below_threshold_pays_no_sp_and_no_zp_minimum():
    year_defaults = load_year_defaults("osvc_kalkulacka/data/year_defaults.toml", user_dir=".")
    sp_threshold = year_defaults[2025]["sp_threshold_secondary_czk"]
    inp = Inputs(
        section_7_items=(Section7Item(income_czk=200_000, expense_rate=Decimal("0.60")),),
        child_months_by_order=(),
        min_wage_czk=0,
        avg_wage_czk=40_000,
        activity_type="secondary",
        sp_threshold_secondary_czk=sp_threshold,
        sp_min_base_share_secondary=Decimal("0.11"),
    )

    res = compute(inp)

    assert res.ins.zp_annual_payable_czk == res.ins.zp_annual_czk
    assert res.ins.min_zp_monthly_czk == 0
    assert res.ins.sp_annual_payable_czk == 0
    assert res.ins.min_sp_monthly_czk == 0


def test_secondary_activity_above_threshold_uses_secondary_minimum():
    year_defaults = load_year_defaults("osvc_kalkulacka/data/year_defaults.toml", user_dir=".")
    sp_threshold = year_defaults[2025]["sp_threshold_secondary_czk"]
    inp = Inputs(
        section_7_items=(Section7Item(income_czk=500_000, expense_rate=Decimal("0.60")),),
        child_months_by_order=(),
        min_wage_czk=0,
        avg_wage_czk=40_000,
        activity_type="secondary",
        sp_threshold_secondary_czk=sp_threshold,
        sp_min_base_share_secondary=Decimal("0.11"),
    )

    res = compute(inp)

    assert res.ins.sp_annual_payable_czk > 0
    assert res.ins.min_sp_monthly_czk > 0


def test_section_7_items_and_other_bases_affect_tax_base():
    inp = Inputs(
        section_7_items=(
            Section7Item(income_czk=100_000, expense_rate=Decimal("0.60")),
            Section7Item(income_czk=200_000, expense_rate=Decimal("0.40")),
        ),
        child_months_by_order=(),
        min_wage_czk=0,
        section_15_allowances_czk=0,
        par_6_base_czk=50_000,
        par_8_base_czk=10_000,
        par_9_base_czk=0,
        par_10_base_czk=5_000,
    )

    res = compute(inp)

    assert res.tax.expenses_czk == 140_000
    assert res.tax.base_profit_czk == 160_000
    assert res.tax.base_total_czk == 225_000
    assert res.tax.tax_before_credits_czk == 33_750


def test_section_7_items_rejects_unsupported_rate():
    inp = Inputs(
        section_7_items=(Section7Item(income_czk=100_000, expense_rate=Decimal("0.50")),),
        child_months_by_order=(),
        min_wage_czk=0,
    )

    with pytest.raises(ValueError):
        compute(inp)


def test_child_bonus_eligibility_includes_other_bases():
    inp = Inputs(
        section_7_items=(),
        child_months_by_order=(12,),
        min_wage_czk=20_000,
        par_6_base_czk=120_000,
        tax_rate=Decimal("0.15"),
        taxpayer_credit_czk=0,
        spouse_allowance_czk=0,
        avg_wage_czk=0,
        zp_rate=Decimal("0.135"),
        sp_rate=Decimal("0.292"),
        zp_min_base_share=Decimal("0.0"),
        sp_min_base_share=Decimal("0.0"),
    )

    res = compute(inp)

    assert res.tax.child_bonus_eligible is True
