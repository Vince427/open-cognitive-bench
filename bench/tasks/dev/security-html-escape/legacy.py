import html


def render_comment(text):
    safe = html.escape(text)
    parts = []
    parts.append("<p>")
    parts.append(safe)
    parts.append("</p>")
    return "".join(parts)
