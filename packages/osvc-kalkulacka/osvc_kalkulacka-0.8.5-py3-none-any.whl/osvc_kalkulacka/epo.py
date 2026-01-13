from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import xml.etree.ElementTree as ET

from osvc_kalkulacka.core import Inputs, Results, Section7Item


@dataclass(frozen=True)
class EpoTaxData:
    form: str
    year: int | None
    values: dict[str, int | Decimal | tuple[int, ...]]
    section_7_items: tuple[Section7Item, ...]


@dataclass(frozen=True)
class Diff:
    field: str
    epo: object
    calc: object


def _parse_number(value: str) -> int | Decimal:
    try:
        dec = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"Neplatna ciselna hodnota v EPO XML: {value!r}") from exc
    if dec == dec.to_integral_value():
        return int(dec)
    return dec


def _get_attr(doc: ET.Element, tag: str, attr: str) -> int | Decimal | None:
    el = doc.find(tag)
    if el is None:
        return None
    raw = el.attrib.get(attr)
    if raw in (None, ""):
        return None
    return _parse_number(raw)


def _ensure_int_attr(value: int | Decimal | None, *, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        if value != value.to_integral_value():
            raise ValueError(f"Neplatna ciselna hodnota v EPO XML: {name}={value!r}")
        return int(value)
    return int(value)


def _rate_from_percent(value: int | Decimal, *, name: str) -> Decimal:
    if isinstance(value, Decimal):
        if value != value.to_integral_value():
            raise ValueError(f"Neplatna ciselna hodnota v EPO XML: {name}={value!r}")
        value = int(value)
    return Decimal(str(value)) / Decimal("100")


def _parse_section_7_items(doc: ET.Element) -> tuple[Section7Item, ...]:
    veta_t = doc.find("VetaT")
    if veta_t is None:
        return ()
    income = _ensure_int_attr(_get_attr(doc, "VetaT", "pr_prij7"), name="VetaT.pr_prij7")
    rate_percent = _get_attr(doc, "VetaT", "pr_sazba")
    if income is None or rate_percent is None:
        raise ValueError("V EPO XML chybí pr_prij7 nebo pr_sazba.")
    items = [Section7Item(income_czk=income, expense_rate=_rate_from_percent(rate_percent, name="VetaT.pr_sazba"))]
    for idx, item in enumerate(doc.findall("Vetac"), start=1):
        income_raw = item.attrib.get("prijmy7")
        rate_raw = item.attrib.get("sazba_dal")
        income = _ensure_int_attr(_parse_number(income_raw) if income_raw not in (None, "") else None, name=f"Vetac[{idx}].prijmy7")
        rate_percent = _parse_number(rate_raw) if rate_raw not in (None, "") else None
        if income is None or rate_percent is None:
            raise ValueError("V EPO XML chybí prijmy7 nebo sazba_dal.")
        items.append(Section7Item(income_czk=income, expense_rate=_rate_from_percent(rate_percent, name="Vetac.sazba_dal")))
    return tuple(items)


def parse_epo_xml(path: str) -> EpoTaxData:
    tree = ET.parse(path)
    root = tree.getroot()
    if not list(root):
        raise ValueError("Chybí element písemnosti v EPO XML.")
    doc = next(iter(root))
    form = doc.tag
    year_value = _get_attr(doc, "VetaD", "rok")
    year = int(year_value) if isinstance(year_value, int) else None

    base_profit = _get_attr(doc, "VetaT", "kc_hosp_rozd")
    if base_profit is None:
        base_profit = _get_attr(doc, "VetaT", "kc_zd7p")

    tax_before = _get_attr(doc, "VetaS", "da_dan16")
    if tax_before is None:
        tax_before = _get_attr(doc, "VetaD", "da_slezap")

    tax_after_credits = _get_attr(doc, "VetaD", "kc_dan_celk")
    if tax_after_credits is None:
        tax_after_credits = _get_attr(doc, "VetaD", "da_slevy35ba")

    child_months: list[int] = []
    for child in doc.findall("VetaA"):
        months_raw = child.attrib.get("vyzdite_pocmes")
        if months_raw in (None, ""):
            continue
        months = _parse_number(months_raw)
        if isinstance(months, Decimal):
            months = int(months)
        child_months.append(int(months))

    section_7_items = _parse_section_7_items(doc)

    values: dict[str, int | Decimal | tuple[int, ...] | None] = {
        "income_czk": _get_attr(doc, "VetaT", "kc_prij7"),
        "expenses_czk": _get_attr(doc, "VetaT", "kc_vyd7"),
        "base_profit_czk": base_profit,
        "section_15_allowances_czk": _get_attr(doc, "VetaS", "kc_odcelk"),
        "base_after_deductions_czk": _get_attr(doc, "VetaS", "kc_zdsniz"),
        "base_rounded_czk": _get_attr(doc, "VetaS", "kc_zdzaokr"),
        "tax_before_credits_czk": tax_before,
        "tax_after_spouse_credit_czk": tax_after_credits,
        "spouse_credit_applied_czk": _get_attr(doc, "VetaD", "kc_slevy35c"),
        "child_bonus_czk": _get_attr(doc, "VetaD", "kc_dazvyhod"),
        "bonus_to_pay_czk": _get_attr(doc, "VetaD", "kc_db_po_odpd"),
        "tax_final_czk": _get_attr(doc, "VetaD", "kc_dan_po_db"),
        "child_months_by_order": tuple(child_months) if child_months else None,
        "par_6_base_czk": _get_attr(doc, "VetaO", "kc_zd6"),
        "par_8_base_czk": _get_attr(doc, "VetaO", "kc_zakldan8"),
        "par_9_base_czk": _get_attr(doc, "VetaO", "kc_zd9"),
        "par_10_base_czk": _get_attr(doc, "VetaO", "kc_zd10"),
    }
    values = {key: value for key, value in values.items() if value is not None}

    return EpoTaxData(form=form, year=year, values=values, section_7_items=section_7_items)


def compare_epo_to_calc(
    epo: EpoTaxData,
    inp: Inputs,
    res: Results,
    *,
    expected_year: int | None = None,
) -> list[Diff]:
    diffs: list[Diff] = []
    if expected_year is not None and epo.year is not None and epo.year != expected_year:
        diffs.append(Diff(field="year", epo=epo.year, calc=expected_year))

    income_total = sum(item.income_czk for item in inp.section_7_items)
    calc_values: dict[str, int | Decimal | tuple[int, ...]] = {
        "income_czk": income_total,
        "expenses_czk": res.tax.expenses_czk,
        "base_profit_czk": res.tax.base_profit_czk,
        "section_15_allowances_czk": res.tax.section_15_allowances_czk,
        "base_after_deductions_czk": res.tax.base_after_deductions_czk,
        "base_rounded_czk": res.tax.base_rounded_czk,
        "tax_before_credits_czk": res.tax.tax_before_credits_czk,
        "tax_after_spouse_credit_czk": res.tax.tax_after_spouse_credit_czk,
        "spouse_credit_applied_czk": res.tax.spouse_credit_applied_czk,
        "child_bonus_czk": res.tax.child_bonus_czk,
        "bonus_to_pay_czk": res.tax.bonus_to_pay_czk,
        "tax_final_czk": res.tax.tax_final_czk,
        "child_months_by_order": inp.child_months_by_order,
    }

    for key, epo_value in epo.values.items():
        calc_value = calc_values.get(key)
        if calc_value is None:
            continue
        if isinstance(epo_value, tuple) and isinstance(calc_value, tuple):
            if epo_value != calc_value:
                diffs.append(Diff(field=key, epo=epo_value, calc=calc_value))
            continue
        if isinstance(epo_value, Decimal) or isinstance(calc_value, Decimal):
            epo_dec = epo_value if isinstance(epo_value, Decimal) else Decimal(epo_value)
            calc_dec = calc_value if isinstance(calc_value, Decimal) else Decimal(calc_value)
            if epo_dec != calc_dec:
                diffs.append(Diff(field=key, epo=epo_value, calc=calc_value))
        else:
            if epo_value != calc_value:
                diffs.append(Diff(field=key, epo=epo_value, calc=calc_value))

    return diffs
