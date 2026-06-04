import html


def render_comment(text):
    return "<p>" + html.escape(text) + "</p>"
