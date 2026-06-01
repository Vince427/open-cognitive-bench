def version_ge(a, b):
    # Compare as integer tuples per component. "1.10.0" >= "1.9.0" must be True.
    # (Direct string comparison would say "1.10.0" < "1.9.0" because '1' < '9' at the 3rd char.)
    pa = [int(x) for x in a.split(".")]
    pb = [int(x) for x in b.split(".")]
    return pa >= pb
