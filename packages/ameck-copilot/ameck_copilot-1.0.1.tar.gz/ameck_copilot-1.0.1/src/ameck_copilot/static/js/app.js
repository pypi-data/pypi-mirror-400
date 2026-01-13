/**
 * Ameck Copilot - Frontend Application
 * AI-powered coding assistant interface
 */

class AmeckCopilot {
    constructor() {
        this.conversationHistory = [];
        this.isStreaming = false;
        this.currentView = 'chat';
        this.selectedModel = 'llama-3.3-70b-versatile';
        
        this.init();
    }
    
    init() {
        this.bindElements();
        this.bindEvents();
        this.setupMarkdown();
    }
    
    bindElements() {
        // Navigation
        this.navBtns = document.querySelectorAll('.nav-btn');
        this.views = document.querySelectorAll('.view');
        
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.modeSelect = document.getElementById('modeSelect');
        this.currentMode = 'ask';
        
        // Code analysis elements
        this.codeInput = document.getElementById('codeInput');
        this.languageSelect = document.getElementById('languageSelect');
        this.opBtns = document.querySelectorAll('.op-btn');
        this.analysisResult = document.getElementById('analysisResult');
        
        // Generate elements
        this.generatePrompt = document.getElementById('generatePrompt');
        this.generateLanguage = document.getElementById('generateLanguage');
        this.generateFramework = document.getElementById('generateFramework');
        this.generateBtn = document.getElementById('generateBtn');
        this.generatedCode = document.getElementById('generatedCode');
        
        // Model selector
        this.modelSelect = document.getElementById('modelSelect');
        
        // Mode selector
        this.modeSelect.addEventListener('change', (e) => this.changeMode(e.target.value));
        
        // Loading overlay
        this.loadingOverlay = document.getElementById('loadingOverlay');
    }
    
    bindEvents() {
        // Navigation
        this.navBtns.forEach(btn => {
            btn.addEventListener('click', () => this.switchView(btn.dataset.view));
        });
        
        // Chat
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keydown', (e) => this.handleInputKeydown(e));
        this.chatInput.addEventListener('input', () => this.autoResizeTextarea());
        this.newChatBtn.addEventListener('click', () => this.startNewChat());
        
        // Code analysis
        this.opBtns.forEach(btn => {
            btn.addEventListener('click', () => this.analyzeCode(btn.dataset.operation));
        });
        
        // Generate
        this.generateBtn.addEventListener('click', () => this.generateCode());
        
        // Model selector
        this.modelSelect.addEventListener('change', (e) => this.changeModel(e.target.value));
        
        // Capability cards
        document.querySelectorAll('.capability-card').forEach(card => {
            card.addEventListener('click', () => {
                this.chatInput.focus();
            });
        });
    }
    
    setupMarkdown() {
        // Configure marked options
        marked.setOptions({
            highlight: (code, lang) => {
                if (lang && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                }
                return hljs.highlightAuto(code).value;
            },
            breaks: true,
            gfm: true
        });
    }
    
    switchView(viewName) {
        this.currentView = viewName;
        
        // Update nav buttons
        this.navBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === viewName);
        });
        
        // Update views
        this.views.forEach(view => {
            view.classList.toggle('active', view.id === `${viewName}View`);
        });
    }
    
    handleInputKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }
    
    autoResizeTextarea() {
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 200) + 'px';
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || this.isStreaming) return;
        
        // Clear input
        this.chatInput.value = '';
        this.chatInput.style.height = 'auto';
        
        // Hide welcome message if present
        const welcomeMsg = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
        
        // Add user message to UI
        this.addMessage('user', message);
        
        // Add to conversation history
        this.conversationHistory.push({
            role: 'user',
            content: message
        });
        
        // Create assistant message container for streaming
        const assistantMessage = this.createMessageElement('assistant', '');
        this.chatMessages.appendChild(assistantMessage);
        const contentDiv = assistantMessage.querySelector('.message-content');
        
        // Add typing indicator
        contentDiv.innerHTML = this.getTypingIndicator();
        this.scrollToBottom();
        
        try {
            this.isStreaming = true;
            this.sendBtn.disabled = true;
            
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    conversation_history: this.conversationHistory.slice(0, -1), // Exclude current message
                    stream: true,
                    model: this.selectedModel,
                    mode: this.currentMode
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullContent = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            
                            if (data.error) {
                                contentDiv.innerHTML = this.renderMarkdown(`**Error:** ${data.error}`);
                                break;
                            }
                            
                            if (data.content) {
                                fullContent += data.content;
                                contentDiv.innerHTML = this.renderMarkdown(fullContent);
                                this.scrollToBottom();
                            }
                            
                            if (data.done) {
                                // Add to conversation history
                                this.conversationHistory.push({
                                    role: 'assistant',
                                    content: fullContent
                                });

                                // If Plan mode, attempt to extract structured JSON and render it
                                if (this.currentMode === 'plan') {
                                    const structured = this.extractJSONFromText(fullContent);
                                    if (structured) {
                                        this.renderStructuredPlan(contentDiv, structured);
                                    }
                                }

                                // If Edit mode and content looks like a unified diff, add download button
                                if (this.currentMode === 'edit') {
                                    if (/^---\s|^diff --git/m.test(fullContent)) {
                                        this.addPatchDownload(contentDiv, fullContent);
                                    }
                                }
                            }
                        } catch (parseError) {
                            // Ignore parse errors for incomplete JSON
                        }
                    }
                }
            }
            
            // Add copy buttons to code blocks
            this.addCopyButtons(contentDiv);
            
        } catch (error) {
            console.error('Error:', error);
            contentDiv.innerHTML = this.renderMarkdown(`**Error:** ${error.message}`);
        } finally {
            this.isStreaming = false;
            this.sendBtn.disabled = false;
        }
    }
    
    addMessage(role, content) {
        const messageEl = this.createMessageElement(role, content);
        this.chatMessages.appendChild(messageEl);
        this.scrollToBottom();
    }
    
    createMessageElement(role, content) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        
        const avatarIcon = role === 'user' 
            ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
            : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>';
        
        div.innerHTML = `
            <div class="message-avatar">
                ${avatarIcon}
            </div>
            <div class="message-content">
                ${content ? this.renderMarkdown(content) : ''}
            </div>
        `;
        
        if (content) {
            this.addCopyButtons(div.querySelector('.message-content'));
        }
        
        return div;
    }
    
    renderMarkdown(content) {
        // Parse markdown and wrap code blocks
        let html = marked.parse(content);
        
        // Add wrapper and header to code blocks
        html = html.replace(/<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g, (match, lang, code) => {
            return `
                <div class="code-block-wrapper">
                    <div class="code-block-header">
                        <span class="code-block-language">${lang}</span>
                        <button class="copy-btn" onclick="app.copyCode(this)">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                            </svg>
                            Copy
                        </button>
                    </div>
                    <pre><code class="language-${lang}">${code}</code></pre>
                </div>
            `;
        });
        
        // Handle code blocks without language
        html = html.replace(/<pre><code>([\s\S]*?)<\/code><\/pre>/g, (match, code) => {
            return `
                <div class="code-block-wrapper">
                    <div class="code-block-header">
                        <span class="code-block-language">code</span>
                        <button class="copy-btn" onclick="app.copyCode(this)">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                            </svg>
                            Copy
                        </button>
                    </div>
                    <pre><code>${code}</code></pre>
                </div>
            `;
        });
        
        return html;
    }
    
    addCopyButtons(container) {
        // Re-highlight code blocks
        container.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
    }

    extractJSONFromText(text) {
        const idx = text.indexOf('JSON:');
        if (idx === -1) return null;
        const after = text.slice(idx + 'JSON:'.length);
        const start = after.indexOf('[');
        const end = after.lastIndexOf(']');
        if (start === -1 || end === -1) return null;
        const jsonStr = after.slice(start, end + 1);
        try {
            return JSON.parse(jsonStr);
        } catch (e) {
            return null;
        }
    }

    renderStructuredPlan(container, structured) {
        // structured expected to be an array of step objects
        const wrapper = document.createElement('div');
        wrapper.className = 'structured-plan';
        const title = document.createElement('h3');
        title.textContent = 'Plan (parsed)';
        wrapper.appendChild(title);

        const list = document.createElement('ol');
        for (const step of structured) {
            const li = document.createElement('li');
            const strong = document.createElement('strong');
            strong.textContent = step.title || `Step ${step.id || ''}`;
            li.appendChild(strong);

            const p = document.createElement('p');
            p.textContent = step.description || '';
            li.appendChild(p);

            if (step.estimate) {
                const est = document.createElement('div');
                est.className = 'estimate';
                est.textContent = `Estimate: ${step.estimate}`;
                li.appendChild(est);
            }
            list.appendChild(li);
        }

        wrapper.appendChild(list);
        container.appendChild(wrapper);
    }

    addPatchDownload(container, patchText) {
        const btn = document.createElement('button');
        btn.className = 'download-patch-btn';
        btn.textContent = 'Download Patch';
        btn.addEventListener('click', () => {
            const blob = new Blob([patchText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'patch.diff';
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        });
        container.appendChild(btn);
    }
    
    copyCode(button) {
        const wrapper = button.closest('.code-block-wrapper');
        const code = wrapper.querySelector('code').textContent;
        
        navigator.clipboard.writeText(code).then(() => {
            const originalText = button.innerHTML;
            button.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"/>
                </svg>
                Copied!
            `;
            setTimeout(() => {
                button.innerHTML = originalText;
            }, 2000);
        });
    }
    
    getTypingIndicator() {
        return `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    changeModel(model) {
        this.selectedModel = model;
        console.log(`Model changed to: ${model}`);
    }

    changeMode(mode) {
        this.currentMode = mode;
        console.log(`Mode changed to: ${mode}`);
        // Adjust placeholder for user convenience
        const placeholders = {
            'ask': 'Ask me anything about code...',
            'agent': 'Describe the goal and constraints, and I will propose actions...',
            'edit': 'Paste code or text to edit and describe desired changes...',
            'plan': 'Describe the project or goal and I will produce a plan...'
        };
        this.chatInput.placeholder = placeholders[mode] || placeholders['ask'];
    }
    
    startNewChat() {
        this.conversationHistory = [];
        this.chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                        <path d="M2 17l10 5 10-5"/>
                        <path d="M2 12l10 5 10-5"/>
                    </svg>
                </div>
                <h2>Welcome to Ameck Copilot</h2>
                <p>I'm your AI coding assistant powered by FREE models via Groq. I can help you with:</p>
                <div class="capability-grid">
                    <div class="capability-card">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="16 18 22 12 16 6"/>
                            <polyline points="8 6 2 12 8 18"/>
                        </svg>
                        <span>Write Code</span>
                    </div>
                    <div class="capability-card">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                            <line x1="12" y1="17" x2="12.01" y2="17"/>
                        </svg>
                        <span>Explain Code</span>
                    </div>
                    <div class="capability-card">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <line x1="12" y1="18" x2="12" y2="12"/>
                            <line x1="9" y1="15" x2="15" y2="15"/>
                        </svg>
                        <span>Debug Issues</span>
                    </div>
                    <div class="capability-card">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 20h9"/>
                            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
                        </svg>
                        <span>Review Code</span>
                    </div>
                </div>
            </div>
        `;
        this.currentMode = 'ask';
        if (this.modeSelect) this.modeSelect.value = 'ask';
        this.chatInput.placeholder = 'Ask me anything about code...';
    }
    
    async analyzeCode(operation) {
        const code = this.codeInput.value.trim();
        if (!code) {
            alert('Please enter some code to analyze.');
            return;
        }
        
        const language = this.languageSelect.value || null;
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/chat/code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: code,
                    operation: operation,
                    language: language,
                    model: this.selectedModel
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.analysisResult.innerHTML = this.renderMarkdown(data.result);
            this.addCopyButtons(this.analysisResult);
            
        } catch (error) {
            console.error('Error:', error);
            this.analysisResult.innerHTML = this.renderMarkdown(`**Error:** ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    async generateCode() {
        const prompt = this.generatePrompt.value.trim();
        if (!prompt) {
            alert('Please describe what you want to generate.');
            return;
        }
        
        const language = this.generateLanguage.value;
        const framework = this.generateFramework.value.trim() || null;
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/chat/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: prompt,
                    language: language,
                    framework: framework,
                    model: this.selectedModel
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.generatedCode.innerHTML = this.renderMarkdown(data.code);
            this.addCopyButtons(this.generatedCode);
            
        } catch (error) {
            console.error('Error:', error);
            this.generatedCode.innerHTML = this.renderMarkdown(`**Error:** ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }
    
    showLoading() {
        this.loadingOverlay.classList.add('active');
    }
    
    hideLoading() {
        this.loadingOverlay.classList.remove('active');
    }
}

// Initialize the application
const app = new AmeckCopilot();
