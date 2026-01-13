# OSVČ kalkulačka (DPFO + ZP/SP)

OSVČ kalkulačka spočítá daň z příjmu fyzických osob a zálohy na zdravotní i sociální pojištění.

## Proč další kalkulačka?

Podobné kalkulačky:

- https://www.kalkulackaosvc.cz
- https://www.kurzy.cz/kalkulacka/kalkulacka-osvc.htm
- https://www.penize.cz/kalkulacky/danova-kalkulacka-osvc
- https://martinmatousek.github.io/kpp/

1) Nevyplňuješ znovu to samé
Kalkulačku můžeš používat z příkazové řádky nebo přes jednoduchý konfigurační soubor. Jednou zadané údaje si pamatuje a zůstávají bezpečně uložené jen u tebe v počítači.

2) Pracuje s více roky
Umí počítat pro různé roky a snadno porovnat výsledky mezi nimi, ne jen aktuální období.

## Instalace

PyPI: https://pypi.org/project/osvc-kalkulacka/

```bash
python3 -m venv .venv
.venv/bin/pip install osvc-kalkulacka
```

```bash
uv tool install osvc-kalkulacka
```

```bash
pipx install osvc-kalkulacka
```

Aktualizace:

```bash
.venv/bin/pip install --upgrade osvc-kalkulacka
```

```bash
uv tool upgrade osvc-kalkulacka
```

```bash
pipx upgrade osvc-kalkulacka
```

## Postup použití

1) Vytvoř předvolby pro roky, se kterými počítáš:

```bash
osvc presets template --output-default
```

```bash
~/.config/osvc-kalkulacka/year_presets.toml
```

2) Doplň `year_presets.toml` (příjmy, děti, nezdanitelné části…). Minimálně potřebuješ `section_7_items` pro daný rok. Výchozí cesta je `~/.config/osvc-kalkulacka/year_presets.toml` a ověříš ji přes `osvc config path`.

Pokud máš XML z EPO, můžeš si presety vygenerovat automaticky:

```bash
osvc presets import-epo --epo ./dpfo_2022.xml --output ~/.config/osvc-kalkulacka/year_presets.jan_novak.toml
osvc presets import-epo --epo ./dpfo_2023.xml --output ~/.config/osvc-kalkulacka/year_presets.jan_novak.toml
osvc presets import-epo --epo ./dpfo_2024.xml --output ~/.config/osvc-kalkulacka/year_presets.jan_novak.toml
```

Pokud v cílovém souboru už rok existuje, použij `--force`.

Příklad obsahu:

```toml
["2025"]
section_7_items = [
  { income_czk = 400000, expense_rate = 0.60 }
  { income_czk = 50000, expense_rate = 0.40 }
]
par_6_base_czk = 300000
par_8_base_czk = 15000
par_9_base_czk = 0
par_10_base_czk = 20000
section_15_allowances_czk = 150000
child_months_by_order = [6, 12]
spouse_allowance = true
activity = "primary"
```

Hodnota `child_months_by_order` je seznam měsíců nároku podle pořadí dítěte (1., 2., 3+). Zápis `child_months_by_order = [6, 12]` znamená 1. dítě 6 měsíců, 2. dítě 12 měsíců.

3) Volitelně pracuj s výchozími parametry výpočtu přes `osvc defaults`, detaily v [ADVANCED_USAGE.md](https://github.com/fertek/osvc-kalkulacka/blob/main/ADVANCED_USAGE.md).

4) Spusť výpočet jen s `--year`, pokud máš v předvolbách vše potřebné:

```bash
osvc --year 2025
```

5) Když chceš přepsat hodnoty z předvoleb, zadej je přímo:

```bash
osvc --year 2025 --section7 income=800000,rate=0.60 --child-months-by-order 12 --activity primary
```

Pokud chceš použít jiný preset soubor, zadej ho přes `--presets`:

```bash
osvc --year 2024 --presets ~/.config/osvc-kalkulacka/year_presets.jan_novak.toml
```

## Ověření s EPO XML

Pokud máš export XML z EPO (DPFDP6/DPFDP7) z https://adisspr.mfcr.cz/pmd/epo/formulare, můžeš ověřit, že kalkulačka vyšla stejně jako podané přiznání.

```bash
osvc verify --epo ./dpfo_2024.xml --year 2024
```

## Přehled příkazů

Zobrazení cest:

```bash
osvc config path
```

Očekávané soubory:

```text
~/.config/osvc-kalkulacka/year_presets.toml
```

## Pokročilé použití

Detaily k `osvc defaults` a pokročilé konfiguraci jsou v [ADVANCED_USAGE.md](https://github.com/fertek/osvc-kalkulacka/blob/main/ADVANCED_USAGE.md).

## Omezení kalkulačky (zatím neřešíme)

- Krácení rozhodné částky pro vedlejší činnost podle počtu měsíců výkonu.
- Krácení rozhodné částky při nároku na nemocenské/peněžitou pomoc v mateřství/dlouhodobé ošetřovné u OSVČ.
- Dobrovolná účast na důchodovém pojištění u vedlejší činnosti.
- Paušální režim (paušální daň a související pravidla).
