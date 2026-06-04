import html


def render_comment(text):
    safe = html.escape(text)
    return "<p>" + safe + "</p>"
