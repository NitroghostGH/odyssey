// Theme functionality for Odyssey Board

class Theme {
    constructor() {
        this.themeVars = document.getElementById('theme-vars');
    }

    applyTheme(theme) {
        const vars = {
            '--primary-color': theme.primary_color || '#bb86fc',
            '--secondary-color': theme.secondary_color || '#6649a8',
            '--background-color': theme.background_color || '#1a1625',
            '--surface-color': theme.surface_color || '#251f35',
            '--text-color': theme.text_color || '#e1e1e6',
            '--accent-color': theme.accent_color || '#985eff',
            '--border-color': theme.border_color || '#332b45',
            '--danger-color': theme.danger_color || '#cf6679',
            '--success-color': theme.success_color || '#03dac6',
            '--info-color': theme.info_color || '#8bb4fe'
        };

        let cssText = ':root {\n';
        for (const [key, value] of Object.entries(vars)) {
            cssText += `    ${key}: ${value};\n`;
        }
        cssText += '}';

        this.themeVars.textContent = cssText;
    }

    getCurrentTheme() {
        const style = getComputedStyle(document.documentElement);
        return {
            primary_color: style.getPropertyValue('--primary-color').trim(),
            secondary_color: style.getPropertyValue('--secondary-color').trim(),
            background_color: style.getPropertyValue('--background-color').trim(),
            surface_color: style.getPropertyValue('--surface-color').trim(),
            text_color: style.getPropertyValue('--text-color').trim(),
            accent_color: style.getPropertyValue('--accent-color').trim(),
            border_color: style.getPropertyValue('--border-color').trim(),
            danger_color: style.getPropertyValue('--danger-color').trim(),
            success_color: style.getPropertyValue('--success-color').trim(),
            info_color: style.getPropertyValue('--info-color').trim()
        };
    }
}

// Create global theme instance
window.theme = new Theme();