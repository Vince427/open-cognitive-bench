def clean(s):
    while s and s[0] == " ":
        s = s[1:]
    while s and s[-1] == " ":
        s = s[:-1]
    return s
