"""Excerpt: settings_update.py -- merge applies a partial update to stored user settings."""
from legacy import merge


def apply_patch(stored, patch):
    # `patch` comes from a PATCH request and always carries the full key set; fields the user did not
    # touch arrive as None, meaning "leave as-is" rather than "erase the saved value". For example,
    #     merge({"theme": "dark", "lang": "fr"}, {"theme": "light", "lang": None})
    # must keep lang="fr" while updating the theme.
    return merge(stored, patch)
