from .models_theme import ThemePreference, UserTheme


def active_theme(request):
    """Provide the active theme colors (user preference or latest user theme) globally.

    Returns two context vars:
      - global_active_theme_colors: dict of color keys -> hex values (may be empty)
      - global_active_theme_id: the id of the theme supplying the colors (or None)
    """
    colors = {}
    theme_id = None
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        try:
            pref = user.theme_preference  # reverse OneToOne
        except ThemePreference.DoesNotExist:  # type: ignore[attr-defined]
            pref = None
        if pref and getattr(pref, 'theme', None):
            raw = pref.theme.colors or {}
            # Normalize possible *_color keys to simplified names so template access works
            normalized = {}
            for k, v in raw.items():
                if k.endswith('_color'):
                    base = k[:-6]
                    normalized[base] = v
                else:
                    normalized[k] = v
            colors = normalized
            theme_id = pref.theme.id
        else:
            # Fallback: last updated user-owned theme
            latest = UserTheme.objects.filter(user=user).order_by('-updated_at').first()
            if latest:
                raw = latest.colors or {}
                normalized = {}
                for k, v in raw.items():
                    if k.endswith('_color'):
                        base = k[:-6]
                        normalized[base] = v
                    else:
                        normalized[k] = v
                colors = normalized
                theme_id = latest.id
    # Ensure template always sees all expected keys so defaults only serve as backup
    expected_keys = ['primary','secondary','background','surface','text','accent','border','danger','success','info']
    complete = {k: colors.get(k) for k in expected_keys if colors.get(k)}
    # Build CSS string early for reliable template output
    def val(k, default):
        return complete.get(k, default)
    css_lines = [":root {"]
    css_lines.append(f"    --primary-color: {val('primary', '#bb86fc')};")
    css_lines.append(f"    --secondary-color: {val('secondary', '#6649a8')};")
    css_lines.append(f"    --background-color: {val('background', '#1a1625')};")
    css_lines.append(f"    --surface-color: {val('surface', '#251f35')};")
    css_lines.append(f"    --text-color: {val('text', '#e1e1e6')};")
    css_lines.append(f"    --accent-color: {val('accent', '#985eff')};")
    css_lines.append(f"    --border-color: {val('border', '#332b45')};")
    css_lines.append(f"    --danger-color: {val('danger', '#cf6679')};")
    css_lines.append(f"    --success-color: {val('success', '#03dac6')};")
    css_lines.append(f"    --info-color: {val('info', '#8bb4fe')};")
    css_lines.append("}")
    return {
        'global_active_theme_colors': complete,
        'global_active_theme_id': theme_id,
        'global_theme_css': '\n'.join(css_lines),
    }
