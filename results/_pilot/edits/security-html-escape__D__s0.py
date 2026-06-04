import html


def render_comment(text):
    safe = html.escape(text)
    return f"<p>{safe}</p>"
