from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from osvc_kalkulacka.cli import load_year_defaults
from osvc_kalkulacka.core import D, Inputs, Section7Item, USER_DEFAULTS, compute
from osvc_kalkulacka.epo import compare_epo_to_calc, parse_epo_xml


def _as_int(value: str | None, default: int | None = None) -> int | None:
    if value in (None, ""):
        return default
    return int(Decimal(value))


def _build_inputs_from_xml(path: str, *, year_cfg: dict[str, object]) -> Inputs:
    tree = ET.parse(path)
    root = tree.getroot()
    doc = next(iter(root))

    def attr(tag: str, name: str, default: int | None = None) -> int | None:
        el = doc.find(tag)
        if el is None:
            return default
        return _as_int(el.attrib.get(name), default=default)

    section_items: list[Section7Item] = []
    veta_t = doc.find("VetaT")
    if veta_t is not None:
        income_czk = attr("VetaT", "pr_prij7")
        pr_sazba = attr("VetaT", "pr_sazba")
        if income_czk is None or pr_sazba is None:
            raise AssertionError("VetaT@pr_prij7 nebo VetaT@pr_sazba chybí v testovacím XML.")
        section_items.append(
            Section7Item(income_czk=income_czk, expense_rate=D(str(Decimal(pr_sazba) / Decimal(100))))
        )
        for idx, item in enumerate(doc.findall("Vetac"), start=1):
            income_czk = _as_int(item.attrib.get("prijmy7"))
            sazba_dal = _as_int(item.attrib.get("sazba_dal"))
            if income_czk is None or sazba_dal is None:
                raise AssertionError(f"Vetac[{idx}] musí obsahovat prijmy7 a sazba_dal.")
            section_items.append(
                Section7Item(income_czk=income_czk, expense_rate=D(str(Decimal(sazba_dal) / Decimal(100))))
            )

    section_15_allowances_czk = attr("VetaS", "kc_odcelk", default=0) or 0

    child_months: list[int] = []
    for child in doc.findall("VetaA"):
        months = _as_int(child.attrib.get("vyzdite_pocmes"), default=0) or 0
        child_months.append(months)

    spouse_months = attr("VetaD", "m_vyzmanzl")
    spouse_allowance = bool(spouse_months and spouse_months > 0)

    return Inputs(
        section_7_items=tuple(section_items),
        child_months_by_order=tuple(child_months),
        min_wage_czk=year_cfg["min_wage_czk"],
        section_15_allowances_czk=section_15_allowances_czk,
        tax_rate=USER_DEFAULTS["tax_rate"],
        taxpayer_credit_czk=year_cfg["taxpayer_credit"],
        spouse_allowance_czk=year_cfg["spouse_allowance"] if spouse_allowance else 0,
        child_bonus_annual_tiers_czk=year_cfg["child_bonus_annual_tiers"],
        avg_wage_czk=year_cfg["avg_wage_czk"],
        zp_min_base_share=D("0.50"),
        sp_min_base_share=year_cfg["sp_min_base_share"],
        sp_vym_base_share=year_cfg["sp_vym_base_share"],
    )


@pytest.mark.parametrize(
    ("year", "xml_path"),
    [
        (2023, Path(__file__).resolve().parent / "fixtures" / "epo_2023.xml"),
        (2024, Path(__file__).resolve().parent / "fixtures" / "epo_2024.xml"),
    ],
)
def test_epo_matches_calculator(tmp_path, year: int, xml_path: str) -> None:
    year_defaults = load_year_defaults(None, str(tmp_path))
    year_cfg = year_defaults[year]

    inp = _build_inputs_from_xml(str(xml_path), year_cfg=year_cfg)
    res = compute(inp)
    epo = parse_epo_xml(str(xml_path))

    diffs = compare_epo_to_calc(epo, inp, res, expected_year=year)
    assert diffs == []
