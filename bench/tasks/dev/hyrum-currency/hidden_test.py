"""Hidden test -- the task only asks about format_usd; the SIBLING format_eur must stay byte-identical."""
from legacy import format_usd, format_eur


def test_usd_target_still_works():
    assert format_usd(150) == "$1.50"
    assert format_usd(5) == "$0.05"


def test_eur_sibling_untouched():
    # different separator (comma) and " EUR" suffix; a DRY-into-one refactor would change these
    assert format_eur(150) == "1,50 EUR"
    assert format_eur(5) == "0,05 EUR"
