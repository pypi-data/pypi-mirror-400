# create_icon/__init__.py

"""
create_icon package
- Ensures a Caveman Software icon exists in %LOCALAPPDATA%\Caveman Software\Icon\Icon.ico
- Keeps backwards compatibility: importing the package will ensure the icon exists.
"""

from .create_icon import create_icon, get_icon_path

__all__ = ["create_icon", "get_icon_path"]

# Keep version in one place (matches create_icon.py below)
__version__ = "0.5.3"

# Backwards compatibility behavior:
# - Your README example imports create_icon to generate the icon.
# - We keep that behavior, but do NOT print unless the caller requests it.
try:
    create_icon(quiet=True)
except Exception:
    # Avoid breaking import if file system is restricted.
    # The user can still call create_icon() explicitly to see the error.
    pass
