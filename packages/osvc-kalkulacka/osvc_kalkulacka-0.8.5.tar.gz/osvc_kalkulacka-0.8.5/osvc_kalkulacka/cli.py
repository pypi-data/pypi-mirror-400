from __future__ import annotations

import json
import os
from decimal import Decimal
from importlib import resources
import tomllib

import click

from osvc_kalkulacka.core import (
    D,
    Inputs,
    Section7Item,
    USER_DEFAULTS,
    ceil_czk,
    compute,
    round_czk_half_up,
    validate_section_7_rate,
)
from osvc_kalkulacka.epo import compare_epo_to_calc, parse_epo_xml


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def print_row(label: str, value: int | str, *, suffix: str = "Kč", label_width: int = 40) -> None:
    """
    Print a row with aligned value column. Integers are formatted with thousands separators
    and optional suffix (default Kč); strings are printed as-is.
    """
    if isinstance(value, int):
        value_str = f"{fmt(value)} {suffix}" if suffix else fmt(value)
    else:
        value_str = value
    print(f"{label:<{label_width}}{value_str}")


def print_row_text(label: str, value: str, *, label_width: int = 40) -> None:
    """Print a row where value is already formatted text (no suffix)."""
    print_row(label, value, suffix="", label_width=label_width)


def format_settlement(amount: int) -> str:
    """Format settlement as doplatek/přeplatek text."""
    if amount > 0:
        return f"doplatek {fmt(amount)} Kč"
    if amount < 0:
        return f"přeplatek {fmt(abs(amount))} Kč"
    return "0 Kč"


def get_user_dir() -> str:
    env_path = os.getenv("OSVC_USER_PATH")
    if env_path:
        return env_path
    return click.get_app_dir("osvc-kalkulacka")


def _load_toml(path: str) -> dict[str, object]:
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError as exc:
        raise SystemExit(f"Soubor nenalezen: {path}") from exc


def _load_package_toml(filename: str) -> dict[str, object]:
    try:
        with resources.files("osvc_kalkulacka.data").joinpath(filename).open("rb") as f:
            return tomllib.load(f)
    except FileNotFoundError as exc:
        raise SystemExit(
            f"Chybí defaultní {filename}. Zadej --defaults nebo nastav OSVC_DEFAULTS_PATH."
        ) from exc


def load_year_presets(path: str | None, user_dir: str) -> dict[int, dict[str, object]]:
    """
    Načte roční presety z TOML. Priorita:
    1) explicitní cesta (CLI), 2) OSVC_PRESETS_PATH, 3) {user_dir}/year_presets.toml
    """
    if path:
        data = _load_toml(path)
    else:
        env_path = os.getenv("OSVC_PRESETS_PATH")
        if env_path:
            data = _load_toml(env_path)
        else:
            preset_path = os.path.join(user_dir, "year_presets.toml")
            if not os.path.exists(preset_path):
                raise SystemExit(
                    f"Chybí preset soubor: {preset_path}. Spusť "
                    "`osvc presets template --output-default` nebo zadej --presets."
                )
            data = _load_toml(preset_path)

    out: dict[int, dict[str, object]] = {}
    for key, value in data.items():
        try:
            year_key = int(key)
        except (TypeError, ValueError):
            continue
        if isinstance(value, dict):
            out[year_key] = value
    return out


def _ensure_int(value: object, *, name: str, year: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SystemExit(f"Rok {year}: {name} musí být celé číslo.")
    if value < 0:
        raise SystemExit(f"Rok {year}: {name} nesmí být záporné.")
    return value


def _resolve_paid_amount(
    cli_value: int | None,
    preset: dict[str, object],
    *,
    key: str,
    year: int,
) -> int | None:
    if cli_value is not None:
        return _ensure_int(cli_value, name=key, year=year)
    if key in preset:
        return _ensure_int(preset.get(key), name=key, year=year)
    return None


def _ensure_decimal_0_1(value: object, *, name: str, year: int) -> D:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, str)):
        raise SystemExit(f"Rok {year}: {name} musí být číslo (0.0–1.0).")
    if isinstance(value, Decimal):
        dec = value
    else:
        dec = D(str(value))
    if not (D("0") <= dec <= D("1")):
        raise SystemExit(f"Rok {year}: {name} musí být v intervalu 0.0–1.0.")
    return dec


def _ensure_section_7_rate(value: D, *, name: str, year: int) -> D:
    try:
        validate_section_7_rate(name, value)
    except ValueError as exc:
        raise SystemExit(f"Rok {year}: {name} musí být 0.40, 0.60 nebo 0.80.") from exc
    return value


def _ensure_bool(value: object, *, name: str, year: int) -> bool:
    if not isinstance(value, bool):
        raise SystemExit(f"Rok {year}: {name} musí být true/false.")
    return value


def _ensure_activity(value: object, *, year: int) -> str:
    if not isinstance(value, str):
        raise SystemExit(f"Rok {year}: activity musí být 'primary' nebo 'secondary'.")
    activity = value.strip().lower()
    if activity not in ("primary", "secondary"):
        raise SystemExit(f"Rok {year}: activity musí být 'primary' nebo 'secondary'.")
    return activity


def _parse_section7_item(raw: str, *, year: int) -> Section7Item:
    parts = [part.strip() for part in raw.split(",") if part.strip()]
    if not parts:
        raise SystemExit("section7 položka nesmí být prázdná.")
    data: dict[str, str] = {}
    for part in parts:
        if "=" not in part:
            raise SystemExit("section7 položka musí být ve formátu income=...,rate=... (rate 0.40/0.60/0.80).")
        key, value = part.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key in data:
            raise SystemExit(f"section7 klíč {key!r} je zadán vícekrát.")
        data[key] = value

    allowed_keys = {"income", "rate"}
    unknown = set(data.keys()) - allowed_keys
    if unknown:
        unknown_list = ", ".join(sorted(unknown))
        raise SystemExit(f"section7 položka má neznámé klíče: {unknown_list}")
    if "income" not in data or "rate" not in data:
        raise SystemExit("section7 položka musí obsahovat income a rate (např. income=100000,rate=0.60).")

    try:
        income_raw = int(data["income"])
    except ValueError as exc:
        raise SystemExit("section7 income musí být celé číslo.") from exc
    income_czk = _ensure_int(income_raw, name="section_7_items.income_czk", year=year)
    rate = _ensure_decimal_0_1(data["rate"], name="section_7_items.expense_rate", year=year)
    rate = _ensure_section_7_rate(rate, name="section_7_items.expense_rate", year=year)
    return Section7Item(income_czk=income_czk, expense_rate=rate)


def _parse_section7_items_from_preset(value: object, *, year: int) -> tuple[Section7Item, ...]:
    if not isinstance(value, list):
        raise SystemExit(f"Rok {year}: section_7_items musí být seznam položek.")
    if not value:
        raise SystemExit(f"Rok {year}: section_7_items nesmí být prázdný.")
    items: list[Section7Item] = []
    for idx, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise SystemExit(f"Rok {year}: section_7_items[{idx}] musí být tabulka.")
        unknown = set(item.keys()) - {"income_czk", "expense_rate"}
        if unknown:
            unknown_list = ", ".join(sorted(unknown))
            raise SystemExit(f"Rok {year}: section_7_items[{idx}] neznámé klíče: {unknown_list}")
        if "income_czk" not in item or "expense_rate" not in item:
            raise SystemExit(f"Rok {year}: section_7_items[{idx}] musí mít income_czk a expense_rate.")
        income_czk = _ensure_int(item.get("income_czk"), name="section_7_items.income_czk", year=year)
        rate = _ensure_decimal_0_1(item.get("expense_rate"), name="section_7_items.expense_rate", year=year)
        rate = _ensure_section_7_rate(rate, name="section_7_items.expense_rate", year=year)
        items.append(Section7Item(income_czk=income_czk, expense_rate=rate))
    return tuple(items)


def _ensure_child_months(value: object, *, year: int) -> tuple[int, ...]:
    if not isinstance(value, list):
        raise SystemExit(f"Rok {year}: child_months_by_order musí být seznam čísel.")
    months: list[int] = []
    for idx, item in enumerate(value, start=1):
        month = _ensure_int(item, name="child_months_by_order", year=year)
        if not 0 <= month <= 12:
            raise SystemExit(f"Rok {year}: child_months_by_order[{idx}] musí být 0–12.")
        months.append(month)
    return tuple(months)


def _ensure_int_from_epo(value: object, *, name: str, year: int) -> int:
    if isinstance(value, Decimal):
        if value != value.to_integral_value():
            raise SystemExit(f"Rok {year}: {name} musí být celé číslo.")
        value = int(value)
    if isinstance(value, bool) or not isinstance(value, int):
        raise SystemExit(f"Rok {year}: {name} musí být celé číslo.")
    if value < 0:
        raise SystemExit(f"Rok {year}: {name} nesmí být záporné.")
    return value


def _toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return str(int(value))
        return str(value)
    if isinstance(value, dict):
        parts = []
        for key in sorted(value.keys()):
            parts.append(f"{key} = {_toml_value(value[key])}")
        return "{ " + ", ".join(parts) + " }"
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    if isinstance(value, tuple):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=True)
    raise SystemExit(f"Neznámý typ hodnoty pro TOML: {type(value).__name__}")


def _render_presets_toml(presets: dict[int, dict[str, object]]) -> str:
    lines: list[str] = []
    order = [
        "section_7_items",
        "section_15_allowances_czk",
        "child_months_by_order",
        "spouse_allowance",
        "activity",
        "par_6_base_czk",
        "par_8_base_czk",
        "par_9_base_czk",
        "par_10_base_czk",
    ]
    def render_section_7_items(items: object) -> list[str]:
        if not isinstance(items, (list, tuple)):
            return [f"section_7_items = {_toml_value(items)}"]
        out_lines = ["section_7_items = ["]
        for item in items:
            if isinstance(item, dict) and "income_czk" in item and "expense_rate" in item:
                extra = [key for key in item.keys() if key not in ("income_czk", "expense_rate")]
                if extra:
                    out_lines.append(f"  {_toml_value(item)}")
                else:
                    income = _toml_value(item["income_czk"])
                    rate = _toml_value(item["expense_rate"])
                    out_lines.append(f"  {{ income_czk = {income}, expense_rate = {rate} }}")
            else:
                out_lines.append(f"  {_toml_value(item)}")
        out_lines.append("]")
        return out_lines

    for idx, year in enumerate(sorted(presets)):
        if idx:
            lines.append("")
        lines.append(f"[\"{year}\"]")
        preset = presets[year]
        for key in order:
            if key in preset:
                if key == "section_7_items":
                    lines.extend(render_section_7_items(preset[key]))
                else:
                    lines.append(f"{key} = {_toml_value(preset[key])}")
        extra_keys = sorted(k for k in preset.keys() if k not in order)
        for key in extra_keys:
            lines.append(f"{key} = {_toml_value(preset[key])}")
    lines.append("")
    return "\n".join(lines)


def _normalize_year_presets(data: dict[str, object]) -> dict[int, dict[str, object]]:
    out: dict[int, dict[str, object]] = {}
    for key, value in data.items():
        try:
            year_key = int(key)
        except (TypeError, ValueError):
            continue
        if isinstance(value, dict):
            out[year_key] = value
    return out


def _build_inputs(
    *,
    year: int,
    section_7_items: tuple[str, ...] | None,
    presets: str | None,
    defaults: str | None,
    section_15_allowances: int | None,
    child_months_by_order: str | None,
    spouse_allowance: bool | None,
    activity: str | None,
    par_6_base_czk: int | None,
    par_8_base_czk: int | None,
    par_9_base_czk: int | None,
    par_10_base_czk: int | None,
    paid_tax_czk: int | None,
    paid_zp_czk: int | None,
    paid_sp_czk: int | None,
) -> tuple[Inputs, dict[int, dict[str, object]], dict[str, int | None]]:
    user_dir = get_user_dir()

    year_defaults = load_year_defaults(defaults, user_dir)
    year_cfg = year_defaults.get(year)
    if year_cfg is None:
        known_years = ", ".join(str(y) for y in sorted(year_defaults))
        raise SystemExit(
            f"Neznám daňové parametry pro rok {year}. Známé roky: {known_years}. "
            "Doplň year_defaults.toml."
        )
    if year_cfg["min_wage_czk"] <= 0:
        raise SystemExit(f"Chybí min_wage_czk pro rok {year}. Doplň year_defaults.toml.")

    year_presets = load_year_presets(presets, user_dir)
    preset = year_presets.get(year, {})
    if "income_czk" in preset:
        raise SystemExit("Preset obsahuje income_czk; to už není podporováno. Použij section_7_items.")
    section_7_items_tuple: tuple[Section7Item, ...] | None = None
    if section_7_items:
        section_7_items_tuple = tuple(_parse_section7_item(item, year=year) for item in section_7_items)
    elif "section_7_items" in preset:
        section_7_items_tuple = _parse_section7_items_from_preset(preset.get("section_7_items"), year=year)

    if section_7_items_tuple is None:
        section_7_items_tuple = ()

    if section_15_allowances is not None:
        section_15_allowances_czk = section_15_allowances
    else:
        section_15_allowances_czk = _ensure_int(
            preset.get("section_15_allowances_czk", 0),
            name="section_15_allowances_czk",
            year=year,
        )
    child_months_by_order_tuple = None
    if child_months_by_order:
        child_months_by_order_tuple = _parse_child_months(child_months_by_order)
    elif "child_months_by_order" in preset:
        child_months_by_order_tuple = _ensure_child_months(
            preset.get("child_months_by_order"),
            year=year,
        )

    if child_months_by_order_tuple is None:
        raise SystemExit("Chybí child_months_by_order. Zadej --child-months-by-order nebo nastav preset.")
    if spouse_allowance is True:
        spouse_allowance = True
    elif spouse_allowance is False:
        spouse_allowance = False
    else:
        if "spouse_allowance" in preset:
            spouse_allowance = _ensure_bool(preset.get("spouse_allowance"), name="spouse_allowance", year=year)
        else:
            spouse_allowance = False

    if activity is None:
        if "activity" in preset:
            activity = _ensure_activity(preset.get("activity"), year=year)
        else:
            activity = "primary"
    activity = activity.lower()
    if activity not in ("primary", "secondary"):
        raise SystemExit("activity musí být primary nebo secondary.")

    if par_6_base_czk is None:
        par_6_base_czk = _ensure_int(preset.get("par_6_base_czk", 0), name="par_6_base_czk", year=year)
    if par_8_base_czk is None:
        par_8_base_czk = _ensure_int(preset.get("par_8_base_czk", 0), name="par_8_base_czk", year=year)
    if par_9_base_czk is None:
        par_9_base_czk = _ensure_int(preset.get("par_9_base_czk", 0), name="par_9_base_czk", year=year)
    if par_10_base_czk is None:
        par_10_base_czk = _ensure_int(preset.get("par_10_base_czk", 0), name="par_10_base_czk", year=year)

    paid = {
        "paid_tax_czk": _resolve_paid_amount(paid_tax_czk, preset, key="paid_tax_czk", year=year),
        "paid_zp_czk": _resolve_paid_amount(paid_zp_czk, preset, key="paid_zp_czk", year=year),
        "paid_sp_czk": _resolve_paid_amount(paid_sp_czk, preset, key="paid_sp_czk", year=year),
    }

    return Inputs(
        child_months_by_order=child_months_by_order_tuple,
        min_wage_czk=year_cfg["min_wage_czk"],
        section_7_items=section_7_items_tuple,
        section_15_allowances_czk=section_15_allowances_czk,
        tax_rate=USER_DEFAULTS["tax_rate"],
        taxpayer_credit_czk=year_cfg["taxpayer_credit"],
        spouse_allowance_czk=year_cfg["spouse_allowance"] if spouse_allowance else 0,
        par_6_base_czk=par_6_base_czk,
        par_8_base_czk=par_8_base_czk,
        par_9_base_czk=par_9_base_czk,
        par_10_base_czk=par_10_base_czk,
        child_bonus_annual_tiers_czk=year_cfg["child_bonus_annual_tiers"],
        avg_wage_czk=year_cfg["avg_wage_czk"],
        zp_min_base_share=D("0.50"),
        sp_min_base_share=year_cfg["sp_min_base_share"],
        sp_vym_base_share=year_cfg["sp_vym_base_share"],
        sp_min_base_share_secondary=year_cfg["sp_min_base_share_secondary"],
        sp_threshold_secondary_czk=year_cfg["sp_threshold_secondary_czk"],
        activity_type=activity,
    ), year_defaults, paid


def load_year_defaults(path: str | None, user_dir: str) -> dict[int, dict[str, object]]:
    """
    Načte roční tabulky z TOML. Priorita:
    1) explicitní cesta (CLI), 2) OSVC_DEFAULTS_PATH, 3) {user_dir}/year_defaults.override.toml (pokud existuje),
    4) default v balíčku.
    """
    if path:
        data = _load_toml(path)
    else:
        env_path = os.getenv("OSVC_DEFAULTS_PATH")
        if env_path:
            data = _load_toml(env_path)
        else:
            override_path = os.path.join(user_dir, "year_defaults.override.toml")
            if os.path.exists(override_path):
                data = _load_toml(override_path)
            else:
                data = _load_package_toml("year_defaults.toml")

    required_keys = {
        "avg_wage_czk",
        "min_wage_czk",
        "taxpayer_credit",
        "child_bonus_annual_tiers",
        "spouse_allowance",
        "sp_vym_base_share",
        "sp_min_base_share",
        "sp_min_base_share_secondary",
        "sp_threshold_secondary_czk",
    }

    out: dict[int, dict[str, object]] = {}
    for key, value in data.items():
        try:
            year_key = int(key)
        except (TypeError, ValueError):
            raise SystemExit(f"Neplatný klíč roku: {key!r}")
        if not isinstance(value, dict):
            raise SystemExit(f"Rok {year_key}: očekávám tabulku s hodnotami.")

        unknown_keys = set(value.keys()) - required_keys
        if unknown_keys:
            unknown_list = ", ".join(sorted(unknown_keys))
            raise SystemExit(f"Rok {year_key}: neznámé klíče: {unknown_list}")

        missing_keys = required_keys - set(value.keys())
        if missing_keys:
            missing_list = ", ".join(sorted(missing_keys))
            raise SystemExit(f"Rok {year_key}: chybí klíče: {missing_list}")

        avg_wage_czk = _ensure_int(value["avg_wage_czk"], name="avg_wage_czk", year=year_key)
        min_wage_czk = _ensure_int(value["min_wage_czk"], name="min_wage_czk", year=year_key)
        taxpayer_credit = _ensure_int(value["taxpayer_credit"], name="taxpayer_credit", year=year_key)
        spouse_allowance = _ensure_int(value["spouse_allowance"], name="spouse_allowance", year=year_key)

        tiers = value["child_bonus_annual_tiers"]
        if not isinstance(tiers, list) or len(tiers) != 3:
            raise SystemExit(f"Rok {year_key}: child_bonus_annual_tiers musí být pole se 3 čísly.")
        child_tiers = tuple(_ensure_int(item, name="child_bonus_annual_tiers", year=year_key) for item in tiers)

        sp_vym_base_share = _ensure_decimal_0_1(value["sp_vym_base_share"], name="sp_vym_base_share", year=year_key)
        sp_min_base_share = _ensure_decimal_0_1(value["sp_min_base_share"], name="sp_min_base_share", year=year_key)
        sp_min_base_share_secondary = _ensure_decimal_0_1(
            value["sp_min_base_share_secondary"], name="sp_min_base_share_secondary", year=year_key
        )
        sp_threshold_secondary_czk = _ensure_int(
            value["sp_threshold_secondary_czk"], name="sp_threshold_secondary_czk", year=year_key
        )

        out[year_key] = {
            "avg_wage_czk": avg_wage_czk,
            "min_wage_czk": min_wage_czk,
            "taxpayer_credit": taxpayer_credit,
            "spouse_allowance": spouse_allowance,
            "child_bonus_annual_tiers": child_tiers,
            "sp_vym_base_share": sp_vym_base_share,
            "sp_min_base_share": sp_min_base_share,
            "sp_min_base_share_secondary": sp_min_base_share_secondary,
            "sp_threshold_secondary_czk": sp_threshold_secondary_czk,
        }

    return out


def _parse_child_months(raw: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in raw.split(",") if item.strip())


def _json_dump(payload: object) -> None:
    click.echo(json.dumps(payload, ensure_ascii=True, indent=2, default=str))


def _results_as_dict(
    inp: Inputs,
    res,
    *,
    paid: dict[str, int | None] | None = None,
    next_year: int | None = None,
    next_year_min_zp_monthly_czk: int | None = None,
    next_year_min_sp_monthly_czk: int | None = None,
    zp_post_overview_monthly_czk: int | None = None,
    sp_post_overview_monthly_czk: int | None = None,
) -> dict[str, object]:
    paid_values = paid or {"paid_tax_czk": None, "paid_zp_czk": None, "paid_sp_czk": None}
    tax_paid = paid_values["paid_tax_czk"] if paid_values["paid_tax_czk"] is not None else 0
    zp_paid = paid_values["paid_zp_czk"]
    sp_paid = paid_values["paid_sp_czk"]
    zp_settlement_base = zp_paid if zp_paid is not None else res.ins.zp_annual_prescribed_czk
    sp_settlement_base = sp_paid if sp_paid is not None else res.ins.sp_annual_prescribed_czk
    tax_settlement = res.tax.tax_final_czk - tax_paid
    zp_settlement = res.ins.zp_annual_payable_czk - zp_settlement_base
    sp_settlement = res.ins.sp_annual_payable_czk - sp_settlement_base
    settlement_is_estimate = any(value is None for value in paid_values.values())
    zp_settlement_basis = "paid" if zp_paid is not None else "prescribed"
    sp_settlement_basis = "paid" if sp_paid is not None else "prescribed"
    tax_settlement_basis = "paid" if paid_values["paid_tax_czk"] is not None else "prescribed"
    return {
        "inputs": {
            "activity_type": inp.activity_type,
            "section_7_items": [
                {"income_czk": item.income_czk, "expense_rate": str(item.expense_rate)}
                for item in inp.section_7_items
            ],
            "child_months_by_order": list(inp.child_months_by_order),
            "min_wage_czk": inp.min_wage_czk,
            "section_15_allowances_czk": inp.section_15_allowances_czk,
            "tax_rate": str(inp.tax_rate),
            "taxpayer_credit_czk": inp.taxpayer_credit_czk,
            "spouse_allowance_czk": inp.spouse_allowance_czk,
            "par_6_base_czk": inp.par_6_base_czk,
            "par_8_base_czk": inp.par_8_base_czk,
            "par_9_base_czk": inp.par_9_base_czk,
            "par_10_base_czk": inp.par_10_base_czk,
            "child_bonus_annual_tiers_czk": list(inp.child_bonus_annual_tiers_czk),
            "avg_wage_czk": inp.avg_wage_czk,
            "zp_rate": str(inp.zp_rate),
            "sp_rate": str(inp.sp_rate),
            "zp_vym_base_share": str(inp.zp_vym_base_share),
            "sp_vym_base_share": str(inp.sp_vym_base_share),
            "zp_min_base_share": str(inp.zp_min_base_share),
            "sp_min_base_share": str(inp.sp_min_base_share),
            "sp_min_base_share_secondary": str(inp.sp_min_base_share_secondary),
            "sp_threshold_secondary_czk": inp.sp_threshold_secondary_czk,
        },
        "tax": {
            "expenses_czk": res.tax.expenses_czk,
            "base_profit_czk": res.tax.base_profit_czk,
            "other_base_czk": res.tax.other_base_czk,
            "base_total_czk": res.tax.base_total_czk,
            "section_15_allowances_czk": res.tax.section_15_allowances_czk,
            "base_after_deductions_czk": res.tax.base_after_deductions_czk,
            "base_rounded_czk": res.tax.base_rounded_czk,
            "tax_before_credits_czk": res.tax.tax_before_credits_czk,
            "tax_after_taxpayer_credit_czk": res.tax.tax_after_taxpayer_credit_czk,
            "tax_after_spouse_credit_czk": res.tax.tax_after_spouse_credit_czk,
            "spouse_credit_applied_czk": res.tax.spouse_credit_applied_czk,
            "child_bonus_czk": res.tax.child_bonus_czk,
            "child_bonus_eligible": res.tax.child_bonus_eligible,
            "child_bonus_min_income_czk": res.tax.child_bonus_min_income_czk,
            "tax_final_czk": res.tax.tax_final_czk,
            "bonus_to_pay_czk": res.tax.bonus_to_pay_czk,
            "paid_tax_czk": paid_values["paid_tax_czk"],
            "tax_settlement_czk": tax_settlement,
            "tax_settlement_basis": tax_settlement_basis,
        },
        "insurance": {
            "vym_base_czk": res.ins.vym_base_czk,
            "min_zp_monthly_czk": res.ins.min_zp_monthly_czk,
            "min_sp_monthly_czk": res.ins.min_sp_monthly_czk,
            "zp_annual_czk": res.ins.zp_annual_czk,
            "zp_monthly_calc_czk": res.ins.zp_monthly_calc_czk,
            "zp_monthly_payable_czk": res.ins.zp_monthly_payable_czk,
            "zp_annual_payable_czk": res.ins.zp_annual_payable_czk,
            "zp_annual_prescribed_czk": res.ins.zp_annual_prescribed_czk,
            "zp_annual_settlement_czk": zp_settlement,
            "zp_settlement_basis": zp_settlement_basis,
            "paid_zp_czk": zp_paid,
            "zp_post_overview_monthly_czk": zp_post_overview_monthly_czk,
            "sp_annual_czk": res.ins.sp_annual_czk,
            "sp_monthly_calc_czk": res.ins.sp_monthly_calc_czk,
            "sp_monthly_payable_czk": res.ins.sp_monthly_payable_czk,
            "sp_annual_payable_czk": res.ins.sp_annual_payable_czk,
            "sp_annual_prescribed_czk": res.ins.sp_annual_prescribed_czk,
            "sp_annual_settlement_czk": sp_settlement,
            "sp_settlement_basis": sp_settlement_basis,
            "paid_sp_czk": sp_paid,
            "sp_post_overview_monthly_czk": sp_post_overview_monthly_czk,
            "next_year_minima": (
                {
                    "year": next_year,
                    "min_zp_monthly_czk": next_year_min_zp_monthly_czk,
                    "min_sp_monthly_czk": next_year_min_sp_monthly_czk,
                }
                if next_year is not None
                else None
            ),
        },
        "settlement": {
            "total_settlement_czk": tax_settlement + zp_settlement + sp_settlement,
            "is_estimate": settlement_is_estimate,
        },
    }


def _render_calc_output(
    inp: Inputs,
    res,
    year: int,
    output_format: str,
    year_defaults: dict[int, dict[str, object]],
    paid: dict[str, int | None],
) -> None:
    next_year = year + 1
    next_year_cfg = year_defaults.get(next_year)
    next_year_min_zp_monthly_czk = None
    next_year_min_sp_monthly_czk = None
    zp_post_overview_monthly_czk = None
    sp_post_overview_monthly_czk = None
    if next_year_cfg is not None:
        avg_wage_czk = next_year_cfg["avg_wage_czk"]
        zp_annual_min = 0
        sp_annual_min = 0
        sp_due_next = True
        if inp.activity_type == "secondary":
            next_year_min_zp_monthly_czk = 0
            sp_due_next = res.tax.base_profit_czk > next_year_cfg["sp_threshold_secondary_czk"]
            if sp_due_next:
                sp_annual_min = ceil_czk(
                    D(str(avg_wage_czk))
                    * next_year_cfg["sp_min_base_share_secondary"]
                    * inp.sp_rate
                    * D("12")
                )
                next_year_min_sp_monthly_czk = ceil_czk(D(sp_annual_min) / D("12"))
            else:
                next_year_min_sp_monthly_czk = 0
        else:
            zp_annual_min = ceil_czk(
                D(str(avg_wage_czk)) * inp.zp_min_base_share * inp.zp_rate * D("12")
            )
            sp_annual_min = ceil_czk(
                D(str(avg_wage_czk)) * next_year_cfg["sp_min_base_share"] * inp.sp_rate * D("12")
            )
            next_year_min_zp_monthly_czk = ceil_czk(D(zp_annual_min) / D("12"))
            next_year_min_sp_monthly_czk = ceil_czk(D(sp_annual_min) / D("12"))
        zp_post_overview_annual = max(res.ins.zp_annual_czk, zp_annual_min)
        zp_post_overview_monthly_czk = ceil_czk(D(zp_post_overview_annual) / D("12")) if zp_post_overview_annual else 0
        if sp_due_next:
            sp_post_overview_annual = max(res.ins.sp_annual_czk, sp_annual_min)
            sp_post_overview_monthly_czk = (
                ceil_czk(D(sp_post_overview_annual) / D("12")) if sp_post_overview_annual else 0
            )
        else:
            sp_post_overview_monthly_czk = 0
    if output_format == "json":
        _json_dump(
            _results_as_dict(
                inp,
                res,
                paid=paid,
                next_year=next_year if next_year_cfg is not None else None,
                next_year_min_zp_monthly_czk=next_year_min_zp_monthly_czk,
                next_year_min_sp_monthly_czk=next_year_min_sp_monthly_czk,
                zp_post_overview_monthly_czk=zp_post_overview_monthly_czk,
                sp_post_overview_monthly_czk=sp_post_overview_monthly_czk,
            )
        )
        return

    tax_paid = paid["paid_tax_czk"] if paid["paid_tax_czk"] is not None else 0
    tax_label = "Doplatek na dani:" if paid["paid_tax_czk"] is not None else "Doplatek na dani (odhad):"
    tax_settlement = res.tax.tax_final_czk - tax_paid

    print("OSVČ kalkulačka – DPFO + pojistné (zjednodušený výpočet)")
    print("-" * 70)
    activity_label = "primary (hlavní)" if inp.activity_type == "primary" else "secondary (vedlejší)"
    print_row_text("Typ činnosti:", activity_label)
    print()

    print("DPFO (daň z příjmů)")
    section_7_income = sum(item.income_czk for item in inp.section_7_items)
    print_row("Příjmy (§7):", section_7_income)
    if inp.section_7_items:
        for idx, item in enumerate(inp.section_7_items, start=1):
            rate_percent = int((item.expense_rate * D("100")).to_integral_value())
            item_expenses = round_czk_half_up(D(item.income_czk) * item.expense_rate)
            print_row(f"  Položka {idx} – příjmy:", item.income_czk)
            print_row(f"  Položka {idx} – výdaje ({rate_percent}%):", item_expenses)
    print_row("Výdaje paušálem (celkem):", res.tax.expenses_czk)
    print_row("Zisk / základ (§7):", res.tax.base_profit_czk)
    if res.tax.other_base_czk > 0:
        print_row("Dílčí základ (§6):", inp.par_6_base_czk)
        print_row("Dílčí základ (§8):", inp.par_8_base_czk)
        print_row("Dílčí základ (§9):", inp.par_9_base_czk)
        print_row("Dílčí základ (§10):", inp.par_10_base_czk)
        print_row("Součet dílčích základů:", res.tax.base_total_czk)
    print()
    print_row("Nezdanitelné části základu daně (§15):", res.tax.section_15_allowances_czk)
    print_row("Základ po odpočtu §15:", res.tax.base_after_deductions_czk)
    print_row("Základ daně zaokrouhlený:", res.tax.base_rounded_czk)
    print()
    print_row("Daň z příjmů před odečtením slev:", res.tax.tax_before_credits_czk)
    print_row("Sleva na poplatníka:", inp.taxpayer_credit_czk)
    print_row("Sleva na manžela/ku (nárok):", inp.spouse_allowance_czk)
    print_row("Sleva na manžela/ku (uplatněno):", res.tax.spouse_credit_applied_czk)
    total_credits_claimed = inp.taxpayer_credit_czk + inp.spouse_allowance_czk
    total_credits_applied = inp.taxpayer_credit_czk + res.tax.spouse_credit_applied_czk
    print_row("Slevy celkem (nárok):", total_credits_claimed)
    print_row("Slevy celkem (uplatněno):", total_credits_applied)
    print_row("Daň po slevách na poplatníka a manžela/ku:", res.tax.tax_after_spouse_credit_czk)
    print()
    if not res.tax.child_bonus_eligible:
        min_income = fmt(res.tax.child_bonus_min_income_czk)
        print(f"VAROVÁNÍ: Daňové zvýhodnění na děti neuplatněno (příjmy < {min_income} Kč).")
    child_used_for_tax = min(res.tax.child_bonus_czk, res.tax.tax_after_spouse_credit_czk)
    print_row("Zvýhodnění na děti (uplatněno):", res.tax.child_bonus_czk)
    print_row("  Z toho použito na snížení daně:", child_used_for_tax)
    print_row("Daňový bonus vyplacený (-):", res.tax.bonus_to_pay_czk)
    print_row("Daň k úhradě po dětech:", res.tax.tax_final_czk)
    if paid["paid_tax_czk"] is not None:
        print_row("Zaplacené zálohy na daň:", paid["paid_tax_czk"])
    print_row_text(tax_label, format_settlement(tax_settlement))

    print("-" * 70)

    print("Pojistné (ZP/SP) – odhad z ročního zisku")
    if inp.activity_type == "primary":
        print("(Pozn.: pokud výpočet vychází pod minimem, platí se minimální zálohy.)")
    else:
        print("(Pozn.: vedlejší činnost – ZP bez minima, SP jen nad rozhodnou částku.)")
    print("Pozn.: Záloha dle přehledu platí od měsíce následujícího po podání přehledu (ZP i SP).")
    print("Pozn.: Od ledna se vždy uplatní nová minimální záloha pro daný rok.")
    print("Pozn.: Zálohy do podání přehledu vycházejí z posledního přehledu nebo minima.")
    print_row("Vyměřovací základ (50 % zisku):", res.ins.vym_base_czk)
    print()

    print("Zdravotní pojištění (ZP)")
    print_row("  Ročně (13,5 % z VZ):", res.ins.zp_annual_czk)
    print_row("  Měsíčně vypočteno (roční/12):", res.ins.zp_monthly_calc_czk)
    print_row(f"  Minimální záloha ({year}):", res.ins.min_zp_monthly_czk)
    if next_year_min_zp_monthly_czk is not None:
        print_row(f"  Minimální záloha od 1.1.{next_year}:", next_year_min_zp_monthly_czk)
    print_row(
        f"  Záloha podle přehledu za {year} (od měsíce po podání):",
        zp_post_overview_monthly_czk
        if zp_post_overview_monthly_czk is not None
        else res.ins.zp_monthly_payable_czk,
    )
    print_row("  Pojistné po zohlednění minima:", res.ins.zp_annual_payable_czk)
    print_row("  Předepsané zálohy za rok:", res.ins.zp_annual_prescribed_czk)
    if paid["paid_zp_czk"] is not None:
        print_row("  Zaplacené zálohy za rok:", paid["paid_zp_czk"])
    zp_settlement_base = paid["paid_zp_czk"] if paid["paid_zp_czk"] is not None else res.ins.zp_annual_prescribed_czk
    zp_settlement = res.ins.zp_annual_payable_czk - zp_settlement_base
    zp_label = "  Doplatek po přehledu:" if paid["paid_zp_czk"] is not None else "  Doplatek po přehledu (odhad):"
    print_row_text(zp_label, format_settlement(zp_settlement))
    print()

    print("Sociální pojištění (SP)")
    if inp.activity_type == "secondary":
        print_row("  Rozhodná částka (limit):", inp.sp_threshold_secondary_czk)
    print_row("  Ročně (29,2 % z VZ):", res.ins.sp_annual_czk)
    print_row("  Měsíčně vypočteno (roční/12):", res.ins.sp_monthly_calc_czk)
    print_row(f"  Minimální záloha ({year}):", res.ins.min_sp_monthly_czk)
    if next_year_min_sp_monthly_czk is not None:
        print_row(f"  Minimální záloha od 1.1.{next_year}:", next_year_min_sp_monthly_czk)
    print_row(
        f"  Záloha podle přehledu za {year} (od měsíce po podání):",
        sp_post_overview_monthly_czk
        if sp_post_overview_monthly_czk is not None
        else res.ins.sp_monthly_payable_czk,
    )
    print_row("  Pojistné po zohlednění minima:", res.ins.sp_annual_payable_czk)
    print_row("  Předepsané zálohy za rok:", res.ins.sp_annual_prescribed_czk)
    if paid["paid_sp_czk"] is not None:
        print_row("  Zaplacené zálohy za rok:", paid["paid_sp_czk"])
    sp_settlement_base = paid["paid_sp_czk"] if paid["paid_sp_czk"] is not None else res.ins.sp_annual_prescribed_czk
    sp_settlement = res.ins.sp_annual_payable_czk - sp_settlement_base
    sp_label = "  Doplatek po přehledu:" if paid["paid_sp_czk"] is not None else "  Doplatek po přehledu (odhad):"
    print_row_text(sp_label, format_settlement(sp_settlement))

    print("-" * 70)

    zp_settlement_total = zp_settlement
    sp_settlement_total = sp_settlement
    total_settlement = tax_settlement + zp_settlement_total + sp_settlement_total

    print("Souhrn (ročně)")
    print_row("Daň k úhradě:", res.tax.tax_final_czk)
    if paid["paid_tax_czk"] is not None:
        print_row("Zaplacené zálohy na daň:", paid["paid_tax_czk"])
    print_row("ZP – předepsané zálohy za rok:", res.ins.zp_annual_prescribed_czk)
    if paid["paid_zp_czk"] is not None:
        print_row("ZP – zaplacené zálohy za rok:", paid["paid_zp_czk"])
    print_row("SP – předepsané zálohy za rok:", res.ins.sp_annual_prescribed_czk)
    if paid["paid_sp_czk"] is not None:
        print_row("SP – zaplacené zálohy za rok:", paid["paid_sp_czk"])
    total_label = "Celkem k doplacení:" if all(value is not None for value in paid.values()) else "Celkem k doplacení (odhad):"
    print_row_text(total_label, format_settlement(total_settlement))
    print_row("Bonus k výplatě (odečteno):", res.tax.bonus_to_pay_czk)


@click.group(invoke_without_command=True)
@click.version_option(package_name="osvc-kalkulacka")
@click.option(
    "--year",
    type=int,
    required=False,
    help="Rok daňového přiznání (zdaňovací období). Když není zadán, vezme se z EPO XML.",
)
@click.option(
    "--section7",
    "section_7_items",
    multiple=True,
    help="Položka §7 (opakovatelně). Formát: income=...,rate=...; rate je 0.40/0.60/0.80.",
)
@click.option(
    "--presets",
    type=str,
    default=None,
    help="Cesta k TOML s ročními presety. Alternativně lze použít OSVC_PRESETS_PATH.",
)
@click.option(
    "--defaults",
    type=str,
    default=None,
    help="Cesta k TOML s ročními tabulkami. Alternativně lze použít OSVC_DEFAULTS_PATH.",
)
@click.option(
    "--section-15-allowances",
    type=int,
    default=None,
    help="Nezdanitelné části základu daně (§15) v Kč za rok.",
)
@click.option(
    "--child-months-by-order",
    type=str,
    default=None,
    help="Měsíce nároku podle pořadí dětí (např. 6,6,12 pro 1., 2., 3. dítě).",
)
@click.option(
    "--spouse-allowance/--no-spouse-allowance",
    default=None,
    help="Uplatnit/neuplnit slevu na manžela/ku (přepíše preset).",
)
@click.option(
    "--activity",
    type=click.Choice(["primary", "secondary"], case_sensitive=False),
    default=None,
    help="Typ samostatné výdělečné činnosti (primary/secondary).",
)
@click.option("--par-6-base", type=int, default=None, help="Dílčí základ daně (§6) v Kč.")
@click.option("--par-8-base", type=int, default=None, help="Dílčí základ daně (§8) v Kč.")
@click.option("--par-9-base", type=int, default=None, help="Dílčí základ daně (§9) v Kč.")
@click.option("--par-10-base", type=int, default=None, help="Dílčí základ daně (§10) v Kč.")
@click.option("--paid-tax", type=int, default=None, help="Zaplacené zálohy na daň v Kč za rok.")
@click.option("--paid-zp", type=int, default=None, help="Zaplacené zálohy na ZP v Kč za rok.")
@click.option("--paid-sp", type=int, default=None, help="Zaplacené zálohy na SP v Kč za rok.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    show_default=True,
    help="Výstupní formát.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    year: int | None,
    section_7_items: tuple[str, ...],
    presets: str | None,
    defaults: str | None,
    section_15_allowances: int | None,
    child_months_by_order: str | None,
    spouse_allowance: bool | None,
    activity: str | None,
    par_6_base: int | None,
    par_8_base: int | None,
    par_9_base: int | None,
    par_10_base: int | None,
    paid_tax: int | None,
    paid_zp: int | None,
    paid_sp: int | None,
    output_format: str,
) -> None:
    """OSVČ kalkulačka (DPFO + ZP/SP), zjednodušený výpočet."""
    if ctx.invoked_subcommand:
        return
    if year is None:
        raise click.UsageError("Chybí --year. Zadej rok výpočtu.")

    inp, year_defaults, paid = _build_inputs(
        year=year,
        section_7_items=section_7_items,
        presets=presets,
        defaults=defaults,
        section_15_allowances=section_15_allowances,
        child_months_by_order=child_months_by_order,
        spouse_allowance=spouse_allowance,
        activity=activity,
        par_6_base_czk=par_6_base,
        par_8_base_czk=par_8_base,
        par_9_base_czk=par_9_base,
        par_10_base_czk=par_10_base,
        paid_tax_czk=paid_tax,
        paid_zp_czk=paid_zp,
        paid_sp_czk=paid_sp,
    )
    res = compute(inp)
    _render_calc_output(inp, res, year, output_format, year_defaults, paid)


@cli.command()
@click.option("--year", type=int, required=False, help="Rok daňového přiznání (zdaňovací období).")
@click.option("--epo", "epo_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option(
    "--section7",
    "section_7_items",
    multiple=True,
    help="Položka §7 (opakovatelně). Formát: income=...,rate=...; rate je 0.40/0.60/0.80.",
)
@click.option(
    "--presets",
    type=str,
    default=None,
    help="Cesta k TOML s ročními presety. Alternativně lze použít OSVC_PRESETS_PATH.",
)
@click.option(
    "--defaults",
    type=str,
    default=None,
    help="Cesta k TOML s ročními tabulkami. Alternativně lze použít OSVC_DEFAULTS_PATH.",
)
@click.option(
    "--section-15-allowances",
    type=int,
    default=None,
    help="Nezdanitelné části základu daně (§15) v Kč za rok.",
)
@click.option(
    "--child-months-by-order",
    type=str,
    default=None,
    help="Měsíce nároku podle pořadí dětí (např. 6,6,12 pro 1., 2., 3. dítě).",
)
@click.option(
    "--spouse-allowance/--no-spouse-allowance",
    default=None,
    help="Uplatnit/neuplnit slevu na manžela/ku (přepíše preset).",
)
@click.option(
    "--activity",
    type=click.Choice(["primary", "secondary"], case_sensitive=False),
    default=None,
    help="Typ samostatné výdělečné činnosti (primary/secondary).",
)
@click.option("--par-6-base", type=int, default=None, help="Dílčí základ daně (§6) v Kč.")
@click.option("--par-8-base", type=int, default=None, help="Dílčí základ daně (§8) v Kč.")
@click.option("--par-9-base", type=int, default=None, help="Dílčí základ daně (§9) v Kč.")
@click.option("--par-10-base", type=int, default=None, help="Dílčí základ daně (§10) v Kč.")
def verify(
    year: int | None,
    epo_path: str,
    section_7_items: tuple[str, ...],
    presets: str | None,
    defaults: str | None,
    section_15_allowances: int | None,
    child_months_by_order: str | None,
    spouse_allowance: bool | None,
    activity: str | None,
    par_6_base: int | None,
    par_8_base: int | None,
    par_9_base: int | None,
    par_10_base: int | None,
) -> None:
    epo = parse_epo_xml(epo_path)
    if year is None:
        if epo.year is None:
            raise SystemExit("Chybí --year a EPO XML nemá rok.")
        year = epo.year
    inp, _year_defaults, _paid = _build_inputs(
        year=year,
        section_7_items=section_7_items,
        presets=presets,
        defaults=defaults,
        section_15_allowances=section_15_allowances,
        child_months_by_order=child_months_by_order,
        spouse_allowance=spouse_allowance,
        activity=activity,
        par_6_base_czk=par_6_base,
        par_8_base_czk=par_8_base,
        par_9_base_czk=par_9_base,
        par_10_base_czk=par_10_base,
        paid_tax_czk=None,
        paid_zp_czk=None,
        paid_sp_czk=None,
    )
    res = compute(inp)
    diffs = compare_epo_to_calc(epo, inp, res, expected_year=year)

    def fmt_value(value: object) -> str:
        if isinstance(value, int):
            return fmt(value)
        return str(value)

    print(f"EPO formulář: {epo.form}")
    if epo.year is not None:
        print(f"Rok v EPO: {epo.year}")
    if not diffs:
        print("OK: Výpočty odpovídají EPO.")
        return

    print("NESHODA: nalezeny rozdíly:")
    for diff in diffs:
        epo_value = fmt_value(diff.epo) if diff.epo is not None else "-"
        calc_value = fmt_value(diff.calc) if diff.calc is not None else "-"
        print(f"- {diff.field}: EPO={epo_value} vs kalkulačka={calc_value}")

@cli.group()
def config() -> None:
    """Konfigurace a cesty."""


@config.command("path")
def config_path() -> None:
    """Vypíše user dir a očekávané cesty."""
    user_dir = get_user_dir()
    preset_path = os.path.join(user_dir, "year_presets.toml")
    defaults_override = os.path.join(user_dir, "year_defaults.override.toml")
    click.echo(f"user_dir: {user_dir}")
    click.echo(f"presets: {preset_path}")
    click.echo(f"defaults_override: {defaults_override}")
    if os.getenv("OSVC_USER_PATH"):
        click.echo(f"OSVC_USER_PATH: {os.getenv('OSVC_USER_PATH')}")
    if os.getenv("OSVC_PRESETS_PATH"):
        click.echo(f"OSVC_PRESETS_PATH: {os.getenv('OSVC_PRESETS_PATH')}")
    if os.getenv("OSVC_DEFAULTS_PATH"):
        click.echo(f"OSVC_DEFAULTS_PATH: {os.getenv('OSVC_DEFAULTS_PATH')}")


@cli.group()
def presets() -> None:
    """Práce s ročními presety."""


@presets.command("template")
@click.option("--output", type=click.Path(dir_okay=False, writable=True), default=None)
@click.option("--output-default", is_flag=True, help="Zapsat do {user_dir}/year_presets.toml.")
@click.option("--force", is_flag=True, help="Přepsat existující preset soubor.")
def presets_template(output: str | None, output_default: bool, force: bool) -> None:
    """Vypíše nebo uloží šablonu presetů."""
    if output and output_default:
        raise SystemExit("Nelze kombinovat --output a --output-default.")
    data = resources.files("osvc_kalkulacka.data").joinpath("year_presets.example.toml").read_bytes()
    if output_default:
        user_dir = get_user_dir()
        os.makedirs(user_dir, exist_ok=True)
        output = os.path.join(user_dir, "year_presets.toml")
    if output is None:
        click.echo(data.decode("utf-8"), nl=True)
        return
    if os.path.exists(output) and not force:
        raise SystemExit(f"Soubor už existuje: {output}. Použij --force.")
    with open(output, "wb") as f:
        f.write(data)
    click.echo(f"Zapsáno: {output}")


@presets.command("import-epo")
@click.option("--epo", "epo_path", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option(
    "--output",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Výstupní TOML (zapsat do zadaného souboru; bez outputu se vypisuje na stdout).",
)
@click.option(
    "--output-default",
    is_flag=True,
    help="Zapsat do {user_dir}/year_presets.toml.",
)
@click.option("--force", is_flag=True, help="Přepsat existující rok v preset souboru.")
@click.option(
    "--activity",
    type=click.Choice(["primary", "secondary"], case_sensitive=False),
    default=None,
    help="Typ samostatné výdělečné činnosti (primary/secondary).",
)
def presets_import_epo(
    epo_path: str,
    output: str | None,
    force: bool,
    activity: str | None,
    output_default: bool,
) -> None:
    """Importuje DAP (EPO XML) jako preset; §7 se mapuje na section_7_items."""
    if output and output_default:
        raise SystemExit("Nelze kombinovat --output a --output-default.")
    epo = parse_epo_xml(epo_path)
    if epo.year is None:
        raise SystemExit("V EPO XML chybí rok.")

    values = epo.values
    section_7_items = [
        {"income_czk": item.income_czk, "expense_rate": item.expense_rate}
        for item in epo.section_7_items
    ]

    section_15_raw = values.get("section_15_allowances_czk", 0)
    section_15_allowances_czk = _ensure_int_from_epo(
        section_15_raw,
        name="section_15_allowances_czk",
        year=epo.year,
    )

    child_raw = values.get("child_months_by_order")
    if child_raw is None:
        child_months_by_order = []
    elif isinstance(child_raw, tuple):
        child_months_by_order = list(_ensure_child_months(list(child_raw), year=epo.year))
    else:
        raise SystemExit("V EPO XML má child_months_by_order neplatný formát.")

    spouse_credit_raw = values.get("spouse_credit_applied_czk")
    if spouse_credit_raw is None:
        spouse_allowance = False
    elif isinstance(spouse_credit_raw, (int, Decimal)):
        spouse_allowance = spouse_credit_raw > 0
    else:
        raise SystemExit("V EPO XML má spouse_credit_applied_czk neplatný formát.")

    par_6_base_raw = values.get("par_6_base_czk", 0) or 0
    par_8_base_raw = values.get("par_8_base_czk", 0) or 0
    par_9_base_raw = values.get("par_9_base_czk", 0) or 0
    par_10_base_raw = values.get("par_10_base_czk", 0) or 0

    par_6_base_czk = _ensure_int_from_epo(par_6_base_raw, name="par_6_base_czk", year=epo.year)
    par_8_base_czk = _ensure_int_from_epo(par_8_base_raw, name="par_8_base_czk", year=epo.year)
    par_9_base_czk = _ensure_int_from_epo(par_9_base_raw, name="par_9_base_czk", year=epo.year)
    par_10_base_czk = _ensure_int_from_epo(par_10_base_raw, name="par_10_base_czk", year=epo.year)

    preset: dict[str, object] = {
        "section_7_items": section_7_items,
        "section_15_allowances_czk": section_15_allowances_czk,
        "child_months_by_order": child_months_by_order,
        "spouse_allowance": spouse_allowance,
        "par_6_base_czk": par_6_base_czk,
        "par_8_base_czk": par_8_base_czk,
        "par_9_base_czk": par_9_base_czk,
        "par_10_base_czk": par_10_base_czk,
    }
    if activity is not None:
        preset["activity"] = activity.lower()

    if output_default:
        user_dir = get_user_dir()
        os.makedirs(user_dir, exist_ok=True)
        output = os.path.join(user_dir, "year_presets.toml")
    if output is None:
        click.echo(_render_presets_toml({epo.year: preset}), nl=True)
        return

    if os.path.exists(output):
        data = _load_toml(output)
        presets_data = _normalize_year_presets(data)
        if epo.year in presets_data and not force:
            raise SystemExit(f"Rok {epo.year} už v {output} existuje. Použij --force.")
    else:
        presets_data = {}
    presets_data[epo.year] = preset
    with open(output, "w", encoding="utf-8") as f:
        f.write(_render_presets_toml(presets_data))
    click.echo(f"Zapsáno: {output}")


@cli.command("defaults")
@click.option("--output", type=click.Path(dir_okay=False, writable=True), default=None)
def defaults_dump(output: str | None) -> None:
    """Vypíše výchozí parametry výpočtu (year_defaults.toml); s --output je uloží do souboru."""
    data = resources.files("osvc_kalkulacka.data").joinpath("year_defaults.toml").read_bytes()
    if output:
        with open(output, "wb") as f:
            f.write(data)
        click.echo(f"Zapsáno: {output}")
    else:
        click.echo(data.decode("utf-8"), nl=True)


if __name__ == "__main__":
    cli()
