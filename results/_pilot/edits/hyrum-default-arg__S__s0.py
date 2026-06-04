def render(items, sep=", "):
    return sep.join(items)


def render_lines(items):
    return render(items, sep="\n")
