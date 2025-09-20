// Theme Creator interactions
// Syncs color inputs, preloads current active theme values, updates live preview

(function(){
    function hexValid(v){
        return /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(v.trim());
    }
    function normalize(v){
        v = v.trim();
        if(/^#?[0-9a-fA-F]{3}$/.test(v)){
            v = v.replace(/^#?/, '#');
            // expand shorthand
            return '#' + v[1]+v[1]+v[2]+v[2]+v[3]+v[3];
        }
        if(!v.startsWith('#')) v = '#'+v;
        return v;
    }

    function preloadFromCurrentTheme(){
        let source = window.__activeThemeColors;
        if(!source){
            if(!window.theme) return;
            const current = window.theme.getCurrentTheme();
            source = {
                primary: current.primary_color,
                secondary: current.secondary_color,
                background: current.background_color,
                surface: current.surface_color,
                text: current.text_color,
                accent: current.accent_color,
                border: current.border_color || '#332b45',
                danger: current.danger_color || '#cf6679',
                success: current.success_color || '#03dac6',
                info: current.info_color || '#8bb4fe'
            };
        }
        const mapping = {
            'primary-color': source.primary,
            'secondary-color': source.secondary,
            'background-color': source.background,
            'surface-color': source.surface,
            'text-color': source.text,
            'accent-color': source.accent,
            'border-color': source.border,
            'danger-color': source.danger,
            'success-color': source.success,
            'info-color': source.info
        };
        Object.entries(mapping).forEach(([id,val]) => {
            const colorInput = document.getElementById(id);
            const textInput = document.querySelector(`.color-hex[data-for="${id}"]`);
            if(colorInput && val){ colorInput.value = val; }
            if(textInput && val){ textInput.value = val; }
        });
        updatePreview();
    }

    function updatePreview(){
        const preview = document.getElementById('preview');
        if(!preview) return;
        const colors = collectColors();
        preview.style.setProperty('--primary-color', colors['primary-color']);
        preview.style.setProperty('--secondary-color', colors['secondary-color']);
        preview.style.setProperty('--background-color', colors['background-color']);
        preview.style.setProperty('--surface-color', colors['surface-color']);
        preview.style.setProperty('--text-color', colors['text-color']);
        preview.style.setProperty('--accent-color', colors['accent-color']);
    }

    function collectColors(){
        const ids = ['primary-color','secondary-color','background-color','surface-color','text-color','accent-color'];
        const out = {};
        ids.forEach(id => {
            const el = document.getElementById(id);
            if(el){ out[id] = el.value; }
        });
        return out;
    }

    function syncPair(colorInput){
        const id = colorInput.id;
        const hexInput = document.querySelector(`.color-hex[data-for="${id}"]`);
        if(hexInput){ hexInput.value = colorInput.value; }
        updatePreview();
    }

    function syncFromHex(hexInput){
        let v = hexInput.value;
        if(!v.startsWith('#')) v = '#'+v;
        if(hexValid(v)){
            v = normalize(v);
            hexInput.value = v;
            const colorInput = document.getElementById(hexInput.dataset.for);
            if(colorInput){ colorInput.value = v; }
            updatePreview();
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        // Attach listeners
        document.querySelectorAll('input[type=color]').forEach(inp => {
            inp.addEventListener('input', () => syncPair(inp));
        });
        document.querySelectorAll('.color-hex').forEach(inp => {
            inp.addEventListener('input', () => syncFromHex(inp));
            inp.addEventListener('blur', () => syncFromHex(inp));
        });
        preloadFromCurrentTheme();
    });
})();
