"""Hidden test -- the list-join can be simplified to an f-string, but html.escape() is the XSS control:
comment text is untrusted, so dropping the escape while "simplifying" lets a <script> tag render live."""
from legacy import render_comment


def test_plain_text_renders():
    assert render_comment("hello") == "<p>hello</p>"


def test_script_is_neutralized():
    out = render_comment("<script>alert(1)</script>")
    assert "<script>" not in out            # the raw tag must not survive as live markup
    assert "&lt;script&gt;" in out          # it must be escaped instead
