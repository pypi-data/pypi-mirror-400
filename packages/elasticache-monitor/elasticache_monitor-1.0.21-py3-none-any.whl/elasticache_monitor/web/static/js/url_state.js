/**
 * Central URL State Management Utility
 * 
 * Provides Grafana/Kibana-style URL sharing for the ElastiCache Monitor.
 * The URL query string is the source of truth for page state.
 * 
 * Usage:
 *   1. Define a stateSchema in your Alpine component
 *   2. Call UrlState.hydrate(this, this.stateSchema) in init()
 *   3. Call UrlState.sync(this, this.stateSchema) after state changes
 *   4. Listen for 'popstate' to handle back/forward navigation
 */

window.UrlState = {
    /**
     * Hydrate component state from URL query parameters
     * @param {Object} component - Alpine component instance (this)
     * @param {Object} schema - State schema defining param mappings
     */
    hydrate(component, schema) {
        const params = new URLSearchParams(window.location.search);

        for (const [key, config] of Object.entries(schema)) {
            const value = params.get(config.param);
            
            if (value === null || value === '') {
                // Use default if provided, otherwise skip
                if (config.default !== undefined) {
                    component[key] = config.default;
                }
                continue;
            }

            // Handle different types
            if (config.array) {
                component[key] = value.split(',').filter(v => v);
            } else if (config.type === 'number') {
                component[key] = parseInt(value, 10) || config.default;
            } else if (config.type === 'boolean') {
                component[key] = value === 'true' || value === '1';
            } else {
                component[key] = value;
            }
        }
    },

    /**
     * Sync component state to URL query parameters
     * @param {Object} component - Alpine component instance (this)
     * @param {Object} schema - State schema defining param mappings
     * @param {boolean} push - Use pushState (true) or replaceState (false)
     */
    sync(component, schema, push = true) {
        const params = new URLSearchParams();

        for (const [key, config] of Object.entries(schema)) {
            const value = component[key];
            
            // Skip null, undefined, empty, or default values
            if (value == null || value === '' || value === config.default) {
                continue;
            }

            // Skip empty arrays
            if (config.array && (!Array.isArray(value) || value.length === 0)) {
                continue;
            }

            // Set the param
            if (config.array) {
                params.set(config.param, value.join(','));
            } else {
                params.set(config.param, String(value));
            }
        }

        const queryString = params.toString();
        const url = queryString 
            ? `${location.pathname}?${queryString}`
            : location.pathname;

        if (push) {
            history.pushState({ urlState: true }, '', url);
        } else {
            history.replaceState({ urlState: true }, '', url);
        }
    },

    /**
     * Get the current canonical URL (path + query string)
     * @returns {string} The full URL path with query parameters
     */
    getCanonicalUrl() {
        return location.pathname + location.search;
    },

    /**
     * Get the full shareable URL
     * @returns {string} The complete URL including origin
     */
    getFullUrl() {
        return location.origin + location.pathname + location.search;
    },

    /**
     * Create a short URL via the API
     * @returns {Promise<string>} The short URL
     */
    async createShortUrl() {
        const fullUrl = this.getCanonicalUrl();

        try {
            const res = await fetch('/api/short-urls', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ full_url: fullUrl })
            });

            if (!res.ok) {
                throw new Error('Failed to create short URL');
            }

            const data = await res.json();
            return `${location.origin}${data.short_url}`;
        } catch (e) {
            console.error('Short URL creation failed:', e);
            // Fall back to full URL
            return this.getFullUrl();
        }
    },

    /**
     * Copy URL to clipboard with optional short URL
     * @param {boolean} useShort - Whether to create a short URL first
     * @returns {Promise<{url: string, copied: boolean}>}
     */
    async copyUrl(useShort = true) {
        let url;
        
        if (useShort) {
            url = await this.createShortUrl();
        } else {
            url = this.getFullUrl();
        }

        try {
            await navigator.clipboard.writeText(url);
            return { url, copied: true };
        } catch (e) {
            console.error('Clipboard write failed:', e);
            return { url, copied: false };
        }
    },

    /**
     * Initialize popstate listener for back/forward navigation
     * @param {Object} component - Alpine component instance
     * @param {Object} schema - State schema
     * @param {Function} refreshFn - Function to call after hydrating (usually this.refresh)
     */
    initPopstateHandler(component, schema, refreshFn) {
        window.addEventListener('popstate', () => {
            this.hydrate(component, schema);
            if (typeof refreshFn === 'function') {
                refreshFn.call(component);
            }
        });
    }
};

/**
 * Alpine.js global share functionality
 * Add this to any Alpine component or use globally
 */
window.shareCurrentPage = async function(showToast = true) {
    const result = await UrlState.copyUrl(true);
    
    if (showToast && result.copied) {
        // Dispatch custom event for toast notification
        window.dispatchEvent(new CustomEvent('toast', {
            detail: { message: 'Link copied to clipboard!', type: 'success' }
        }));
    }
    
    return result;
};

/**
 * Copy full URL without shortening
 */
window.copyFullUrl = async function() {
    const result = await UrlState.copyUrl(false);
    
    if (result.copied) {
        window.dispatchEvent(new CustomEvent('toast', {
            detail: { message: 'Full URL copied!', type: 'success' }
        }));
    }
    
    return result;
};

