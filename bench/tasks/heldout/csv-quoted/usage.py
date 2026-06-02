"""Excerpt: import_contacts.py -- split_csv parses a row of an uploaded address book."""
from legacy import split_csv


def parse_contact_row(line):
    # Real rows quote any field that itself contains a comma, e.g. the line
    #     Ada Lovelace,"London, UK",ada@example.com
    # which must parse as exactly three fields: name, location, email.
    name, location, email = split_csv(line)
    return {"name": name, "location": location, "email": email}
