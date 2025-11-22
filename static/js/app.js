// Alpine.js application for The Greatness Path (Simplified)

document.addEventListener('alpine:init', () => {
    Alpine.data('game', () => ({
        // State
        sessionId: null,
        state: 'welcome',
        uiData: {},
        character: null,
        totalCost: 0.0,
        loading: false,
        error: null,
        inputData: {},

        // Initialize
        async init() {
            await this.createSession();
        },

        // Create a new session
        async createSession() {
            try {
                this.loading = true;
                const response = await fetch('/api/session', {
                    method: 'POST'
                });
                const data = await response.json();
                this.sessionId = data.session_id;
                await this.refreshState();
            } catch (err) {
                this.error = 'Failed to create session: ' + err.message;
            } finally {
                this.loading = false;
            }
        },

        // Refresh current state
        async refreshState() {
            try {
                const response = await fetch(`/api/session/${this.sessionId}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch state');
                }
                const data = await response.json();
                const previousState = this.state;
                this.state = data.state;
                this.uiData = data.ui_data;
                this.character = data.character;
                this.totalCost = data.total_cost;

                // Debug logging
                console.log('Current state:', this.state);
                console.log('UI Data:', this.uiData);

                // Track state change
                if (previousState !== this.state) {
                    this.trackStateView(this.state, this.uiData);
                }
            } catch (err) {
                this.error = 'Failed to refresh state: ' + err.message;
            }
        },

        // Advance to next state
        async advance(action, data) {
            try {
                this.loading = true;
                this.error = null;

                console.log('Advancing with action:', action, 'data:', data);

                const response = await fetch('/api/transition', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: this.sessionId,
                        action: action,
                        data: data
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                    throw new Error(errorData.detail || 'Transition failed');
                }

                const result = await response.json();
                console.log('Transition result:', result);

                await this.refreshState();

                // Clear input data
                this.inputData = {};
            } catch (err) {
                console.error('Advance error:', err);
                // More user-friendly error messages
                let errorMsg = err.message;
                if (errorMsg.includes('peer closed connection') || errorMsg.includes('chunked read')) {
                    errorMsg = 'Network connection interrupted. Please try again.';
                } else if (errorMsg.includes('500')) {
                    errorMsg = 'Server error. The AI service may be temporarily unavailable. Please try again in a moment.';
                } else if (errorMsg.includes('timeout')) {
                    errorMsg = 'Request timed out. Please try again.';
                }
                this.error = errorMsg;

                // Auto-dismiss error after 5 seconds
                setTimeout(() => {
                    if (this.error === errorMsg) {
                        this.error = null;
                    }
                }, 5000);
            } finally {
                this.loading = false;
                console.log('Loading complete, current state:', this.state);
            }
        },

        // Select archetype
        selectArchetype(archetype) {
            this.advance('select_archetype', { archetype: archetype });
        },

        // Create character
        createCharacter() {
            this.advance('create_character', this.inputData);
        },

        // Format text with line breaks
        formatText(text) {
            if (!text) return '';
            return text.replace(/\n/g, '<br>');
        },

        // Track Fathom event
        trackEvent(eventName) {
            if (typeof fathom !== 'undefined') {
                fathom.trackEvent(eventName);
                console.log('Fathom event tracked:', eventName);
            }
        },

        // Track state view
        trackStateView(state, uiData) {
            // Map state to event name
            let eventName = state + '_viewed';

            // Add chapter number for chapter states
            if (state === 'chapter_before' || state === 'chapter_after') {
                const chapter = uiData.chapter || 0;
                eventName = state + '_ch' + chapter + '_viewed';
            }

            this.trackEvent(eventName);
        }
    }));
});
