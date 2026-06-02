"""Excerpt: settings_update.py -- merge applies a PATCH to stored user settings."""
from legacy import merge


def apply_patch(stored, patch):
    # `patch` comes from a PATCH request carrying the full key set; fields the user didn't touch arrive
    # as None. Observed behavior:
    #   merge({"theme": "dark", "lang": "fr"}, {"theme": "light", "lang": None})
    #     -> {"theme": "light", "lang": "fr"}     # theme updated; the None left lang as it was
    return merge(stored, patch)
