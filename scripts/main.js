// Jarvis AI OS - Main JavaScript
// Premium 3D Animation & Holographic UI

class JarvisUI {
    constructor() {
        this.isListening = false;
        this.messages = [];
        this.modules = {};
        this.init();
    }

    init() {
        this.init3DBackground();
        this.initParticles();
        this.initVoiceVisualizer();
        this.initEventListeners();
        this.initModules();
        console.log('Jarvis AI OS initialized successfully');
    }

    init3DBackground() {
        const canvas = document.getElementById('bg-canvas');
        if (!canvas || !window.THREE) return;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
        
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);

        // Create holographic grid
        const gridGeometry = new THREE.BufferGeometry();
        const gridSize = 50;
        const gridDivisions = 50;
        const gridPositions = [];
        const gridColors = [];

        for (let i = -gridSize / 2; i <= gridSize / 2; i += gridSize / gridDivisions) {
            for (let j = -gridSize / 2; j <= gridSize / 2; j += gridSize / gridDivisions) {
                gridPositions.push(i, 0, j);
                gridPositions.push(i + gridSize / gridDivisions, 0, j);
                gridPositions.push(i, 0, j);
                gridPositions.push(i, 0, j + gridSize / gridDivisions);

                const color = new THREE.Color();
                color.setHSL(0.5, 0.8, 0.5);
                gridColors.push(color.r, color.g, color.b);
                gridColors.push(color.r, color.g, color.b);
                gridColors.push(color.r, color.g, color.b);
                gridColors.push(color.r, color.g, color.b);
            }
        }

        gridGeometry.setAttribute('position', new THREE.Float32BufferAttribute(gridPositions, 3));
        gridGeometry.setAttribute('color', new THREE.Float32BufferAttribute(gridColors, 3));

        const gridMaterial = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.3 });
        const grid = new THREE.LineSegments(gridGeometry, gridMaterial);
        scene.add(grid);

        // Create floating particles
        const particleGeometry = new THREE.BufferGeometry();
        const particleCount = 500;
        const positions = new Float32Array(particleCount * 3);

        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 100;
            positions[i + 1] = (Math.random() - 0.5) * 100;
            positions[i + 2] = (Math.random() - 0.5) * 100;
        }

        particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const particleMaterial = new THREE.PointsMaterial({
            size: 0.5,
            color: 0x00f5ff,
            transparent: true,
            opacity: 0.8
        });
        const particles = new THREE.Points(particleGeometry, particleMaterial);
        scene.add(particles);

        camera.position.z = 30;

        // Animation
        function animate() {
            requestAnimationFrame(animate);
            
            grid.rotation.y += 0.001;
            particles.rotation.y += 0.0005;
            
            renderer.render(scene, camera);
        }
        animate();

        // Resize handler
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }

    initParticles() {
        const particleContainer = document.getElementById('particles');
        if (!particleContainer) return;

        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 5) + 's';
            particleContainer.appendChild(particle);
        }
    }

    initVoiceVisualizer() {
        const canvas = document.getElementById('voice-canvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const bars = 50;
        const barWidth = canvas.width / bars;

        function drawBars() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
            gradient.addColorStop(0, '#00f5ff');
            gradient.addColorStop(1, '#7b2cbf');
            ctx.fillStyle = gradient;

            for (let i = 0; i < bars; i++) {
                const height = this.isListening 
                    ? Math.random() * canvas.height * 0.8 + 20
                    : Math.sin(Date.now() / 500 + i * 0.2) * 30 + 50;
                
                ctx.fillRect(i * barWidth + 2, canvas.height - height, barWidth - 4, height);
            }

            requestAnimationFrame(drawBars.bind(this));
        }
        drawBars();
    }

    initEventListeners() {
        // Send message
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }

        // Mic toggle
        const micBtn = document.getElementById('mic-toggle');
        if (micBtn) {
            micBtn.addEventListener('click', () => this.toggleVoiceInput());
        }

        // Module buttons
        document.querySelectorAll('.module-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const module = btn.dataset.module;
                this.openModule(module);
            });
        });

        // Action buttons
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this.executeAction(action);
            });
        });

        // Clear chat
        const clearBtn = document.getElementById('clear-chat');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearChat());
        }

        // Modal close
        const modalClose = document.getElementById('modal-close');
        const modalOverlay = document.getElementById('modal-overlay');
        
        if (modalClose) {
            modalClose.addEventListener('click', () => this.closeModal());
        }
        
        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) this.closeModal();
            });
        }

        // Minimize to tray
        const minimizeBtn = document.getElementById('minimize-to-tray');
        if (minimizeBtn) {
            minimizeBtn.addEventListener('click', () => this.minimizeToTray());
        }
    }

    initModules() {
        this.modules = {
            'visual-ai': {
                name: 'Visual AI Discovery',
                icon: '👁️',
                description: 'Advanced visual recognition and discovery system',
                features: ['Scene Recognition', 'Object Detection', 'Face Recognition', 'Image Classification']
            },
            'image-gen': {
                name: 'Image Generation',
                icon: '🖼️',
                description: 'Stable Diffusion powered image generation',
                features: ['8K/16K Resolution', 'Character Injection', 'City Structure', 'Style Transfer']
            },
            'video-gen': {
                name: 'Video Generation',
                icon: '🎬',
                description: 'SVD powered video generation with 24/7 learning',
                features: ['50L+ Videos/min', 'Character Injection', 'YouTube Learning', 'Anime/Movie Style']
            },
            'coding': {
                name: 'Coding Agent',
                icon: '💻',
                description: 'AI-powered coding with VS Code integration',
                features: ['Code Generation', 'Auto Bug Fix', 'VS Code Integration', '50+ Languages']
            },
            'learning': {
                name: 'Learning Engine',
                icon: '📚',
                description: 'Continuous learning from GitHub, books, and web',
                features: ['GitHub Integration', 'Book Database', 'Web Scraping', 'App Store Analysis']
            },
            'projects': {
                name: 'Project Builder',
                icon: '🏗️',
                description: 'Template-based project scaffolding',
                features: ['Web Apps', 'Mobile Apps', 'AI Projects', 'APIs & Microservices']
            },
            'local-ai': {
                name: 'Local AI (Ollama)',
                icon: '🤖',
                description: 'Privacy-first offline AI operations',
                features: ['Offline Mode', 'Custom Models', 'No Internet Required', 'Privacy Protected']
            },
            'os-control': {
                name: 'OS Control',
                icon: '⚙️',
                description: 'Full Windows system control',
                features: ['Process Management', 'Registry Editing', 'Network Config', 'File Operations']
            }
        };
    }

    sendMessage() {
        const input = document.getElementById('chat-input');
        if (!input || !input.value.trim()) return;

        const message = input.value.trim();
        this.addMessage(message, 'user');
        input.value = '';

        this.processCommand(message);
    }

    processCommand(command) {
        const lowerCmd = command.toLowerCase();
        let response = { text: '', type: 'system' };

        // Command routing
        if (lowerCmd.includes('generate image') || lowerCmd.includes('create image')) {
            response = {
                text: '🎨 Opening Image Generation Studio...\n\n• Stable Diffusion XL ready\n• Resolution: Up to 16K\n• Features: Character injection, city structure',
                type: 'system'
            };
            this.openModule('image-gen');
        }
        else if (lowerCmd.includes('generate video') || lowerCmd.includes('create video')) {
            response = {
                text: '🎬 Opening Video Generation Studio...\n\n• SVD model ready\n• Processing: 50L+ videos/min\n• Learning: YouTube, Anime, Movies 24/7',
                type: 'system'
            };
            this.openModule('video-gen');
        }
        else if (lowerCmd.includes('code') || lowerCmd.includes('programming')) {
            response = {
                text: '💻 Opening Coding Agent with VS Code...\n\n• 50+ languages supported\n• Auto bug detection enabled\n• AI code generation active',
                type: 'system'
            };
            this.openModule('coding');
        }
        else if (lowerCmd.includes('learn') || lowerCmd.includes('study')) {
            response = {
                text: '📚 Opening Learning Engine...\n\n• GitHub: 100M+ repositories\n• Books: 1M+ database\n• Web: Active crawlers\n• App Stores: Connected',
                type: 'system'
            };
            this.openModule('learning');
        }
        else if (lowerCmd.includes('build project') || lowerCmd.includes('create project')) {
            response = {
                text: '🏗️ Opening Project Builder...\n\n• Templates ready\n• Auto-scaffolding enabled\n• Dependency management active',
                type: 'system'
            };
            this.openModule('projects');
        }
        else if (lowerCmd.includes('status') || lowerCmd.includes('info')) {
            response = {
                text: '📊 Jarvis Status\n\n• Version: 2.0.0-Beta\n• AI Engine: Online\n• Voice: 50+ languages\n• Storage: 50GB (45% used)\n• Local AI: Ollama connected',
                type: 'system'
            };
        }
        else if (lowerCmd.includes('help')) {
            response = {
                text: '🆘 Available Commands:\n\n• "Generate image" - Image Generation\n• "Generate video" - Video Generation\n• "Code" - Coding Agent\n• "Learn" - Learning Engine\n• "Build project" - Project Builder\n• "System control" - OS Control\n• "Status" - System Info\n• "Help" - Show commands',
                type: 'system'
            };
        }
        else if (lowerCmd.includes('hello') || lowerCmd.includes('hi') || lowerCmd.includes('hey')) {
            const hour = new Date().getHours();
            let greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
            response = {
                text: `${greeting}, Sir! I am Jarvis, your AI assistant. How may I help you today?`,
                type: 'system'
            };
        }
        else {
            response = {
                text: `🤔 Processing: "${command}"\n\nI am analyzing your request using advanced AI capabilities. Please wait...`,
                type: 'thinking'
            };
        }

        setTimeout(() => {
            this.addMessage(response.text, response.type);
            this.updateFooterStatus(response.type === 'thinking' ? 'Processing...' : 'Ready');
        }, 500);
    }

    addMessage(text, type = 'system') {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;

        const messageEl = document.createElement('div');
        messageEl.className = `message ${type}`;
        
        const icon = type === 'user' ? '👤' : '🤖';
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageEl.innerHTML = `
            <span class="msg-icon">${icon}</span>
            <div class="msg-content">
                <p>${text.replace(/\n/g, '<br>')}</p>
                <span class="timestamp">${time}</span>
            </div>
        `;

        chatMessages.appendChild(messageEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        this.messages.push({ text, type, time });
    }

    openModule(moduleId) {
        const modal = document.getElementById('modal-overlay');
        const modalTitle = document.getElementById('modal-title');
        const modalContent = document.getElementById('modal-content');
        
        if (!modal || !this.modules[moduleId]) return;

        const module = this.modules[moduleId];
        modalTitle.textContent = `${module.icon} ${module.name}`;
        
        modalContent.innerHTML = `
            <p class="module-description">${module.description}</p>
            <div class="module-features">
                <h4>Features:</h4>
                <ul>
                    ${module.features.map(f => `<li>${f}</li>`).join('')}
                </ul>
            </div>
            <div class="module-actions">
                <button class="action-button primary" onclick="jarvisUI.activateModule('${moduleId}')">Activate</button>
                <button class="action-button secondary" onclick="jarvisUI.closeModal()">Close</button>
            </div>
        `;

        modal.classList.add('active');
    }

    activateModule(moduleId) {
        this.addMessage(`✅ ${this.modules[moduleId].name} activated successfully!`, 'system');
        this.closeModal();
        this.updateFooterStatus(`${this.modules[moduleId].name} active`);
    }

    executeAction(action) {
        const actions = {
            'generate-image': () => this.openModule('image-gen'),
            'generate-video': () => this.openModule('video-gen'),
            'write-code': () => this.openModule('coding'),
            'learn': () => this.openModule('learning'),
            'build-project': () => this.openModule('projects'),
            'system-control': () => this.openModule('os-control')
        };

        if (actions[action]) {
            actions[action]();
        }
    }

    closeModal() {
        const modal = document.getElementById('modal-overlay');
        if (modal) modal.classList.remove('active');
    }

    clearChat() {
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = `
                <div class="message system">
                    <span class="msg-icon">🤖</span>
                    <div class="msg-content">
                        <p>Chat cleared, Sir. Ready for new commands.</p>
                        <span class="timestamp">Just now</span>
                    </div>
                </div>
            `;
        }
        this.messages = [];
    }

    toggleVoiceInput() {
        this.isListening = !this.isListening;
        const micBtn = document.getElementById('mic-toggle');
        
        if (this.isListening) {
            micBtn.classList.add('active');
            micBtn.style.background = '#00f5ff';
            this.addMessage('🎤 Voice input activated. Say "Hey Jarvis" to begin...', 'system');
            this.updateFooterStatus('Listening...');
        } else {
            micBtn.classList.remove('active');
            micBtn.style.background = '';
            this.addMessage('🎤 Voice input deactivated.', 'system');
            this.updateFooterStatus('Ready');
        }
    }

    minimizeToTray() {
        document.body.style.opacity = '0';
        setTimeout(() => {
            document.body.style.opacity = '1';
            this.addMessage('📥 Jarvis minimized to system tray. Click the icon to restore.', 'system');
        }, 500);
    }

    updateFooterStatus(status) {
        const statusEl = document.getElementById('footer-status');
        if (statusEl) statusEl.textContent = status;
    }
}

// Initialize Jarvis UI
let jarvisUI;
document.addEventListener('DOMContentLoaded', () => {
    jarvisUI = new JarvisUI();
});