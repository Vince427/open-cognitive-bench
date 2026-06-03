def format_usd(cents):
    return f"${cents // 100}.{cents % 100:02d}"


def format_eur(cents):
    return f"{cents // 100},{cents % 100:02d} EUR"
