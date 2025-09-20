// Theme manager functionality for Odyssey Board

class ThemeManager {
    constructor() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Listen for theme change events
        document.addEventListener('theme:change', (e) => {
            if (e.detail && e.detail.theme) {
                window.theme.applyTheme(e.detail.theme);
            }
        });

        // Setup theme selector if it exists
        const themeSelector = document.querySelector('.theme-selector');
        if (themeSelector) {
            themeSelector.addEventListener('change', (e) => {
                this.loadTheme(e.target.value);
            });
        }
    }

    async loadTheme(themeId) {
        if(!themeId){
            // Reset to default? Could implement clearing custom variables.
            this.saveThemePreference('');
            return;
        }
        try {
            const response = await fetch(`/api/themes/${themeId}/`);
            if (!response.ok) throw new Error('Failed to load theme');
            const data = await response.json();
            // Attach raw colors object on window for theme creator prefill
            window.__activeThemeColors = data.colors || {};
            window.theme.applyTheme(data.colors || {});
            this.saveThemePreference(themeId);
        } catch (error) {
            console.error('Error loading theme:', error);
        }
    }

    saveThemePreference(themeId) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) return;

    fetch('/api/themes/set-preference/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ theme_id: themeId })
        }).catch(error => {
            console.error('Error saving theme preference:', error);
        });
    }
}

// Initialize theme manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});