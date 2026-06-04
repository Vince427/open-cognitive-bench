"""Example fact-set for drift-guard. Each entry: (name, fn(module_or_None, source_text) -> bool).
Mix of *code-behavior* checks (need the module) and *rationale/text* checks (source only) — the latter are
what iterative "condense" passes erode first."""

CHECKS = [
    # rationale/text facts (eroded first by "condense" passes)
    ("rationale: SEC-12 present", lambda m, s: "SEC-12" in s),
    ("rationale: INC-2231 present", lambda m, s: "INC-2231" in s),
    # code-behavior facts
    ("MAX_RPM == 100", lambda m, s: getattr(m, "MAX_RPM", None) == 100),
    ("ttl==0 never expires", lambda m, s: m.is_expired({"ttl": 0, "created": 0}, 10 ** 9) is False),
    ("render_comment escapes XSS", lambda m, s: "<script>" not in m.render_comment("<script>")),
    ("join_lines uses sep newline", lambda m, s: m.join_lines(["a", "b"]) == "a\nb"),
    ("recent preserves first-seen order", lambda m, s: m.recent([3, 1, 2, 1, 3]) == [3, 1, 2]),
]
