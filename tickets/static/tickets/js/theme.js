// Theme functionality for Odyssey Board

class Theme {
    constructor() {
        this.themeVars = document.getElementById('theme-vars');
    }

    applyTheme(theme) {
        // Support both API shapes: { primary_color: '#..' } and stored user theme { primary: '#..' }
        function pick(obj, primaryKey, fallbackKey){
            return obj[primaryKey] || obj[fallbackKey];
        }
        const vars = {
            '--primary-color': pick(theme,'primary_color','primary') || '#bb86fc',
            '--secondary-color': pick(theme,'secondary_color','secondary') || '#6649a8',
            '--background-color': pick(theme,'background_color','background') || '#1a1625',
            '--surface-color': pick(theme,'surface_color','surface') || '#251f35',
            '--text-color': pick(theme,'text_color','text') || '#e1e1e6',
            '--accent-color': pick(theme,'accent_color','accent') || '#985eff',
            '--border-color': pick(theme,'border_color','border') || '#332b45',
            '--danger-color': pick(theme,'danger_color','danger') || '#cf6679',
            '--success-color': pick(theme,'success_color','success') || '#03dac6',
            '--info-color': pick(theme,'info_color','info') || '#8bb4fe'
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