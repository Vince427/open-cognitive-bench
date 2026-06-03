import html


def render_comment(text):
    return f"<p>{html.escape(text)}</p>"
