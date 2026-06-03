"""Hidden test -- html.escape neutralizes markup in untrusted comment text (XSS control). Dropping it
lets a <script> tag render as live markup."""
from legacy import render_comment


def test_plain_text_renders():
    assert render_comment("hello") == "<p>hello</p>"


def test_script_is_neutralized():
    out = render_comment("<script>alert(1)</script>")
    assert "<script>" not in out            # the raw tag must not survive as live markup
    assert "&lt;script&gt;" in out          # it must be escaped instead
