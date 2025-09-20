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
        try {
            const response = await fetch(`/api/themes/${themeId}/`);
            if (!response.ok) throw new Error('Failed to load theme');
            
            const theme = await response.json();
            window.theme.applyTheme(theme);
            
            // Save theme preference
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