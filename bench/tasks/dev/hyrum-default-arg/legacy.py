def render(items, sep=", "):
    result = ""
    for i, item in enumerate(items):
        if i > 0:
            result = result + sep
        result = result + item
    return result


def render_lines(items):
    return render(items, sep="\n")
