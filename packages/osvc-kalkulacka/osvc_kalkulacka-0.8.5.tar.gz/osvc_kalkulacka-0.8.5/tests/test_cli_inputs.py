from osvc_kalkulacka import cli


def test_section7_defaults_empty(tmp_path):
    presets_path = tmp_path / "presets.toml"
    presets_path.write_text("", encoding="utf-8")

    inp, _year_defaults, _paid = cli._build_inputs(
        year=2023,
        section_7_items=(),
        presets=str(presets_path),
        defaults="osvc_kalkulacka/data/year_defaults.toml",
        section_15_allowances=None,
        child_months_by_order="0",
        spouse_allowance=None,
        activity=None,
        par_6_base_czk=None,
        par_8_base_czk=None,
        par_9_base_czk=None,
        par_10_base_czk=None,
        paid_tax_czk=None,
        paid_zp_czk=None,
        paid_sp_czk=None,
    )
    assert inp.section_7_items == ()
