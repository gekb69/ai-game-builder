/**
* Multi-Modal Interaction Interface
* Features 76-85: Advanced Communication
*/

class FusionInterface {
    constructor(apiEndpoint = 'http://localhost:8080') {
        this.apiEndpoint = apiEndpoint;
        this.currentMode = 'text';
        this.conversationHistory = [];
        this.isListening = false;
        this.recognition = null;
    }

    initialize() {
        this.setupEventListeners();
        this.setupVoiceRecognition();
    }

    setupEventListeners() {
        const textInput = document.getElementById('text-input');
        if (textInput) {
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.submitText(textInput.value);
                    textInput.value = '';
                }
            });
        }

        const voiceBtn = document.getElementById('voice-btn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleVoiceInput());
        }
    }

    setupVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window)) return;

        this.recognition = new webkitSpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;

        this.recognition.onresult = (event) => {
            const transcript = event.results[event.results.length - 1][0].transcript;
            document.getElementById('voice-transcript').textContent = transcript;
        };
    }

    toggleVoiceInput() {
        if (!this.recognition) return;

        if (this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        } else {
            this.recognition.start();
            this.isListening = true;
        }
    }

    async submitText(text) {
        const response = await fetch(`${this.apiEndpoint}/api/task`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                content: text,
                type: 'general',
                priority: 'medium'
            })
        });

        const result = await response.json();
        this.handleResponse(result);
    }

    handleResponse(response) {
        const output = document.getElementById('response-output');
        if (output) {
            output.innerHTML = `
                <p>${response.status}</p>
            `;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.fusionInterface = new FusionInterface();
});
