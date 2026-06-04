def format_usd(cents):
    dollars, remainder = divmod(cents, 100)
    return f"${dollars}.{remainder:02d}"


def format_eur(cents):
    return f"{cents // 100},{cents % 100:02d} EUR"
