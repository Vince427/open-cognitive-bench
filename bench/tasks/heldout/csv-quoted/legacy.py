def split_csv(line):
    # split on commas, but commas inside double quotes are literal
    out = []
    cur = ""
    inq = False
    for ch in line:
        if ch == '"':
            inq = not inq
        elif ch == "," and not inq:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out
