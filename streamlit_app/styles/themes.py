"""Theme bridge — single source of truth for CSS variables from Python THEME dict."""

from __future__ import annotations

from config.config import THEME

_CSS_VAR_MAP: dict[str, str] = {
    "primary": "--primary",
    "primary_light": "--primary-light",
    "primary_dark": "--primary-dark",
    "success": "--success",
    "warning": "--warning",
    "danger": "--danger",
    "background": "--bg",
    "surface": "--surface",
    "border": "--border",
    "text_primary": "--text",
    "text_secondary": "--text-secondary",
    "text_muted": "--text-muted",
}

_RADIUS_MAP: dict[str, str] = {
    "radius": "12px",
    "radius_sm": "8px",
}

_SHADOW_MAP: dict[str, str] = {
    "shadow": "0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)",
    "shadow_md": "0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04)",
    "shadow_lg": "0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04)",
}


def inject_theme_css() -> str:
    """Return a <style> block that sets CSS custom properties from THEME."""
    parts = [":root {"]
    for key, var_name in _CSS_VAR_MAP.items():
        val = THEME.get(key)
        if val is not None:
            parts.append(f"  {var_name}: {val};")
    for var_name, val in _RADIUS_MAP.items():
        parts.append(f"  --{var_name}: {val};")
    for var_name, val in _SHADOW_MAP.items():
        parts.append(f"  --{var_name}: {val};")
    parts.append("}")
    return "<style>\n" + "\n".join(parts) + "\n</style>"
