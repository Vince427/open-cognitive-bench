def format_usd(cents):
    return "${}.{:02d}".format(cents // 100, cents % 100)


def format_eur(cents):
    return f"{cents // 100},{cents % 100:02d} EUR"
