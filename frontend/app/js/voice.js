// Voice AI Page JavaScript

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initVoiceAnimation();
    setupEventListeners();
    initSpeechRecognition();
});

// Speech recognition variables
let recognition = null;
let isRecording = false;

// Voice animation with canvas
function initVoiceAnimation() {
    const canvas = document.getElementById('voiceCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const container = canvas.parentElement;
    canvas.width = container.clientWidth;
    canvas.height = container.clientHeight;
    
    const particles = [];
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 2 + 1,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5
        });
    }
    
    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(99, 102, 241, 0.5)';
            ctx.fill();
            
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
        });
        
        // Draw connections
        particles.forEach((p1, i) => {
            particles.slice(i + 1).forEach(p2 => {
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(139, 92, 246, ${1 - distance / 100})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            });
        });
        
        requestAnimationFrame(drawParticles);
    }
    
    drawParticles();

    // Handle resize
    window.addEventListener('resize', () => {
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
    });
}

// Setup event listeners
function setupEventListeners() {
    const voiceInput = document.getElementById('voiceInput');
    const voiceSubmitBtn = document.getElementById('voiceSubmitBtn');
    const playAudioBtn = document.getElementById('playAudioBtn');
    const micBtn = document.getElementById('micBtn');

    // Submit button
    if (voiceSubmitBtn && voiceInput) {
        voiceSubmitBtn.addEventListener('click', () => {
            const question = voiceInput.value.trim();
            if (question) {
                handleVoiceQuery(question);
            }
        });
    }

    // Enter key
    if (voiceInput) {
        voiceInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const question = voiceInput.value.trim();
                if (question) {
                    handleVoiceQuery(question);
                }
            }
        });
    }

    // Microphone button
    if (micBtn) {
        micBtn.addEventListener('click', () => {
            toggleSpeechRecognition();
        });
    }

    // Suggestion chips
    const suggestionChips = document.querySelectorAll('.suggestion-chip');
    suggestionChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const question = chip.dataset.question;
            if (voiceInput) voiceInput.value = question;
            handleVoiceQuery(question);
        });
    });

    // Play audio button
    if (playAudioBtn) {
        playAudioBtn.addEventListener('click', () => {
            playVoiceResponse();
        });
    }

    // Notification panel
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationPanel = document.getElementById('notificationPanel');
    const closeNotifications = document.getElementById('closeNotifications');
    
    if (notificationBtn && notificationPanel) {
        notificationBtn.addEventListener('click', () => {
            notificationPanel.classList.add('active');
            loadNotifications();
        });
    }
    
    if (closeNotifications && notificationPanel) {
        closeNotifications.addEventListener('click', () => {
            notificationPanel.classList.remove('active');
        });
    }
}

// Handle voice query
async function handleVoiceQuery(question) {
    const responseContainer = document.getElementById('voiceResponseContainer');
    const responseText = document.getElementById('voiceResponseText');
    const submitBtn = document.getElementById('voiceSubmitBtn');
    const playAudioBtn = document.getElementById('playAudioBtn');

    if (!responseContainer || !responseText || !submitBtn) return;

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    responseContainer.classList.add('active');
    responseText.innerHTML = '<div style="text-align: center;"><i class="fas fa-spinner fa-spin"></i> Thinking with Amazon Nova AI...</div>';

    try {
        const data = await api.askVoice(question);
        
        if (data.success) {
            // Track activity
            if (typeof trackActivity === 'function') {
                trackActivity(
                    'voiceQueries',
                    `Asked: "${question.substring(0, 50)}${question.length > 50 ? '...' : ''}"`,
                    'fas fa-microphone',
                    '#8b5cf6'
                );
            }
            
            // Format the answer nicely - remove markdown and clean up
            let formattedAnswer = data.answer
                .replace(/\*\*/g, '')  // Remove bold markdown
                .replace(/\[(\d+)\]/g, '<sup>[$1]</sup>')  // Format citations
                .replace(/\n\n/g, '</p><p>')  // Convert double newlines to paragraphs
                .trim();
            
            // Wrap in paragraph tags if not already
            if (!formattedAnswer.startsWith('<p>')) {
                formattedAnswer = '<p>' + formattedAnswer + '</p>';
            }
            
            responseText.innerHTML = formattedAnswer;
            
            // Show sources if available
            if (data.sources && data.sources.length > 0) {
                // Filter out localhost URLs for production
                const validSources = data.sources.filter(source => {
                    const url = source.url || '';
                    return !url.includes('localhost') && !url.includes('127.0.0.1');
                });
                
                if (validSources.length > 0) {
                    const sourcesHtml = '<div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.1);">' +
                        '<div style="font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem; color: var(--gray);">Sources:</div>' +
                        validSources.map((source, idx) => {
                            const sourceType = source.source || 'unknown';
                            const sourceTitle = source.title || 'Source';
                            const sourceUrl = source.url || '';
                            
                            // Create clickable link if URL exists
                            if (sourceUrl) {
                                return `<div style="font-size: 0.75rem; color: var(--gray); margin-bottom: 0.25rem;">
                                    [${idx + 1}] <a href="${sourceUrl}" target="_blank" rel="noopener noreferrer" 
                                        style="color: #6366f1; text-decoration: none; hover: text-decoration: underline;">
                                        ${sourceTitle}
                                    </a> <span style="color: var(--gray); font-size: 0.7rem;">(${sourceType})</span>
                                </div>`;
                            } else {
                                return `<div style="font-size: 0.75rem; color: var(--gray); margin-bottom: 0.25rem;">
                                    [${idx + 1}] ${sourceTitle} <span style="color: var(--gray); font-size: 0.7rem;">(${sourceType})</span>
                                </div>`;
                            }
                        }).join('') +
                        '</div>';
                    responseText.innerHTML += sourcesHtml;
                }
            }
            
            // Update play button
            if (playAudioBtn) {
                if (data.audio_available && data.audio_url) {
                    playAudioBtn.disabled = false;
                    playAudioBtn.innerHTML = '<i class="fas fa-volume-up"></i> Play Audio';
                    playAudioBtn.onclick = () => playVoiceResponse(data.audio_url);
                } else {
                    playAudioBtn.disabled = true;
                    playAudioBtn.innerHTML = '<i class="fas fa-volume-mute"></i> Audio Unavailable';
                }
            }
        } else {
            responseText.innerHTML = '<p>Sorry, I encountered an error processing your question. Please try again.</p>';
        }
    } catch (error) {
        console.error('Error asking voice question:', error);
        
        // Fallback to local response generation
        const answer = generateLocalAnswer(question);
        responseText.innerHTML = '<p>' + answer + '</p>';
        
        if (playAudioBtn) {
            playAudioBtn.disabled = true;
            playAudioBtn.innerHTML = '<i class="fas fa-volume-mute"></i> Audio Unavailable';
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Ask';
    }
}

// Generate local answer (fallback)
function generateLocalAnswer(question) {
    const questionLower = question.toLowerCase();
    
    if (questionLower.includes('trending') || questionLower.includes('topic')) {
        return 'Based on current data, the top trending topics in Mumbai are Metro Development, LPG Shortage, and Road Infrastructure. The Metro 3 project is generating significant discussion with high engagement.';
    } else if (questionLower.includes('safety') || questionLower.includes('alert')) {
        return 'There are currently several high-priority safety alerts: Metro 3 bus services have been reduced, and traffic congestion on Ghodbunder Road is being addressed by the Thane civic body. Please check the alerts dashboard for more details.';
    } else if (questionLower.includes('investment') || questionLower.includes('neighborhood')) {
        return 'The best neighborhoods for investment right now are Andheri West (score: 92, trending up), Bandra (score: 88, trending up), and Thane (score: 85, stable). These areas show strong development activity and permit registrations.';
    } else if (questionLower.includes('permit') || questionLower.includes('construction')) {
        return 'Recent permits include Andheri Heights in Andheri West, Bandra Business Park in Bandra East, and GMLR Phase IV in Goregaon-Mulund. You can view the 3D visualization on the Permits page.';
    } else if (questionLower.includes('community') || questionLower.includes('sentiment')) {
        return 'The overall community sentiment is neutral (80%), with 5% positive and 15% negative. Main concerns include airport transport reliability and metro accessibility. Check the Community Pulse page for detailed analysis.';
    } else {
        return 'I can help you with information about Mumbai. Try asking about trending topics, safety alerts, investment neighborhoods, construction permits, or community sentiment.';
    }
}

// Play voice response (real audio)
function playVoiceResponse(audioUrl) {
    if (!audioUrl) {
        alert('No audio available for this response.');
        return;
    }
    
    // Construct proper audio URL
    let fullAudioUrl;
    if (audioUrl.startsWith('http://') || audioUrl.startsWith('https://')) {
        // Already absolute URL
        fullAudioUrl = audioUrl;
    } else {
        // Relative URL - use API base URL from config
        fullAudioUrl = `${API_CONFIG.BASE_URL}${audioUrl}`;
    }
    
    console.log('Playing audio from:', fullAudioUrl);
    
    // Create audio element
    const audio = new Audio(fullAudioUrl);
    
    // Update button during playback
    const playBtn = document.getElementById('playAudioBtn');
    if (playBtn) {
        playBtn.disabled = true;
        playBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Playing...';
    }
    
    audio.onended = () => {
        if (playBtn) {
            playBtn.disabled = false;
            playBtn.innerHTML = '<i class="fas fa-volume-up"></i> Play Audio';
        }
    };
    
    audio.onerror = (error) => {
        console.error('Error playing audio from URL:', fullAudioUrl, error);
        alert(`Error playing audio. Please try again.\nURL attempted: ${fullAudioUrl}`);
        if (playBtn) {
            playBtn.disabled = false;
            playBtn.innerHTML = '<i class="fas fa-volume-up"></i> Play Audio';
        }
    };
    
    audio.play().catch(err => {
        console.error('Audio play() failed:', err);
        alert('Failed to play audio. Please check your browser settings.');
        if (playBtn) {
            playBtn.disabled = false;
            playBtn.innerHTML = '<i class="fas fa-volume-up"></i> Play Audio';
        }
    });
}

// Load notifications
async function loadNotifications() {
    const notificationList = document.getElementById('notificationList');
    if (!notificationList) return;

    try {
        const data = await api.getAlerts();
        const alerts = data.alerts || [];
        const recentAlerts = alerts.slice(0, 5);

        notificationList.innerHTML = recentAlerts.map((alert, index) => `
            <div class="notification-item clickable" data-alert-index="${index}">
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <div style="width: 40px; height: 40px; border-radius: 10px; background: var(--gradient-primary); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        <i class="fas fa-${getSourceIcon(alert.source)}"></i>
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">${alert.title}</div>
                        <div style="color: var(--gray); font-size: 0.875rem; margin-bottom: 0.5rem;">${alert.message.substring(0, 80)}...</div>
                        <div style="color: var(--gray); font-size: 0.75rem;">${formatTime(alert.timestamp)}</div>
                    </div>
                </div>
            </div>
        `).join('');

        // Add click event listeners to notification items
        document.querySelectorAll('.notification-item[data-alert-index]').forEach(item => {
            item.addEventListener('click', (e) => {
                const index = parseInt(item.getAttribute('data-alert-index'));
                handleNotificationClick(index);
            });
        });
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

// Handle notification click
function handleNotificationClick(index) {
    // Close notification panel
    const notificationPanel = document.getElementById('notificationPanel');
    if (notificationPanel) {
        notificationPanel.classList.remove('active');
    }

    // Navigate to alerts page
    window.location.href = 'alerts.html';
}

// Utility functions
function getSourceIcon(source) {
    const icons = {
        'news': 'newspaper',
        'social': 'comments',
        'permit': 'file-alt',
        'image_analysis': 'camera'
    };
    return icons[source] || 'info-circle';
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}


// Initialize speech recognition
function initSpeechRecognition() {
    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.warn('Speech recognition not supported in this browser');
        const micBtn = document.getElementById('micBtn');
        if (micBtn) {
            micBtn.disabled = true;
            micBtn.title = 'Speech recognition not supported in this browser';
        }
        return;
    }
    
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    recognition.onstart = () => {
        isRecording = true;
        const micBtn = document.getElementById('micBtn');
        if (micBtn) {
            micBtn.classList.add('recording');
            micBtn.innerHTML = '<i class="fas fa-stop-circle"></i>';
            micBtn.title = 'Stop recording';
        }
        
        // Show recording indicator
        const voiceInput = document.getElementById('voiceInput');
        if (voiceInput) {
            voiceInput.placeholder = '🎤 Listening...';
        }
    };
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const voiceInput = document.getElementById('voiceInput');
        
        if (voiceInput) {
            voiceInput.value = transcript;
        }
        
        // Automatically submit the question
        handleVoiceQuery(transcript);
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        
        let errorMessage = 'Speech recognition error';
        switch (event.error) {
            case 'no-speech':
                errorMessage = 'No speech detected. Please try again.';
                break;
            case 'audio-capture':
                errorMessage = 'Microphone not found. Please check your device.';
                break;
            case 'not-allowed':
                errorMessage = 'Microphone access denied. Please allow microphone access.';
                break;
            default:
                errorMessage = `Speech recognition error: ${event.error}`;
        }
        
        alert(errorMessage);
        resetMicButton();
    };
    
    recognition.onend = () => {
        resetMicButton();
    };
}

// Toggle speech recognition
function toggleSpeechRecognition() {
    if (!recognition) {
        alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
        return;
    }
    
    if (isRecording) {
        recognition.stop();
    } else {
        try {
            recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            alert('Failed to start speech recognition. Please try again.');
        }
    }
}

// Reset microphone button
function resetMicButton() {
    isRecording = false;
    const micBtn = document.getElementById('micBtn');
    const voiceInput = document.getElementById('voiceInput');
    
    if (micBtn) {
        micBtn.classList.remove('recording');
        micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        micBtn.title = 'Click to speak';
    }
    
    if (voiceInput) {
        voiceInput.placeholder = 'Ask me anything about Mumbai...';
    }
}
