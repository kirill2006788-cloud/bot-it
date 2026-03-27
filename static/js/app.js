// Global variables
let currentGameSession = null;
let currentQuiz = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize password length slider
    const passwordLengthSlider = document.getElementById('password-length');
    const passwordLengthValue = document.getElementById('password-length-value');
    
    if (passwordLengthSlider && passwordLengthValue) {
        passwordLengthSlider.addEventListener('input', function() {
            passwordLengthValue.textContent = this.value;
        });
    }
    
    // Initialize smooth scrolling for navigation
    initializeNavigation();
    
    // Initialize tooltips and other UI elements
    initializeUI();
}

function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            scrollToSection(targetId);
            
            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function initializeUI() {
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.classList.contains('btn-primary')) {
                this.style.opacity = '0.7';
                setTimeout(() => {
                    this.style.opacity = '1';
                }, 1000);
            }
        });
    });
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Password Generator
async function generatePassword() {
    const length = document.getElementById('password-length').value;
    const includeSymbols = document.getElementById('include-symbols').checked;
    const resultDiv = document.getElementById('password-result');
    
    try {
        showLoading(resultDiv);
        
        const response = await fetch('/api/password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                length: parseInt(length),
                include_symbols: includeSymbols
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="success">
                    <strong>🔐 Ваш пароль:</strong><br>
                    <code style="font-size: 1.2rem; font-weight: bold;">${data.password}</code>
                    <button class="copy-btn" onclick="copyToClipboard('${data.password}')">
                        <i class="fas fa-copy"></i> Копировать
                    </button>
                </div>
            `;
        } else {
            showError(resultDiv, data.error);
        }
    } catch (error) {
        showError(resultDiv, 'Ошибка при генерации пароля');
    }
}

// QR Code Generator
async function generateQR() {
    const text = document.getElementById('qr-text').value.trim();
    const resultDiv = document.getElementById('qr-result');
    
    if (!text) {
        showError(resultDiv, 'Введите текст для QR-кода');
        return;
    }
    
    try {
        showLoading(resultDiv);
        
        const response = await fetch('/api/qr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="success">
                    <strong>📱 QR-код создан:</strong><br>
                    <img src="data:image/png;base64,${data.qr_code}" alt="QR Code" style="max-width: 200px; margin: 10px 0;">
                    <br>
                    <button class="copy-btn" onclick="copyToClipboard('${data.text}')">
                        <i class="fas fa-copy"></i> Копировать текст
                    </button>
                </div>
            `;
        } else {
            showError(resultDiv, data.error);
        }
    } catch (error) {
        showError(resultDiv, 'Ошибка при создании QR-кода');
    }
}

// Weather Checker
async function getWeather() {
    const city = document.getElementById('weather-city').value.trim();
    const resultDiv = document.getElementById('weather-result');
    
    if (!city) {
        showError(resultDiv, 'Введите название города');
        return;
    }
    
    try {
        showLoading(resultDiv);
        
        const response = await fetch('/api/weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ city })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const weatherIcon = getWeatherIcon(data.description);
            resultDiv.innerHTML = `
                <div class="success">
                    <strong>🌤️ Погода в ${data.city}:</strong><br>
                    <div style="display: flex; align-items: center; gap: 10px; margin: 10px 0;">
                        <span style="font-size: 2rem;">${weatherIcon}</span>
                        <div>
                            <div style="font-size: 1.5rem; font-weight: bold;">${data.temperature}°C</div>
                            <div style="text-transform: capitalize;">${data.description}</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px;">
                        <div>💧 ${data.humidity}%</div>
                        <div>💨 ${data.wind_speed} м/с</div>
                        <div>📊 ${data.pressure} мм рт.ст.</div>
                    </div>
                </div>
            `;
        } else {
            showError(resultDiv, data.error);
        }
    } catch (error) {
        showError(resultDiv, 'Ошибка при получении данных о погоде');
    }
}

function getWeatherIcon(description) {
    const icons = {
        'ясно': '☀️',
        'облачно': '☁️',
        'дождь': '🌧️',
        'снег': '❄️',
        'туман': '🌫️'
    };
    return icons[description] || '🌤️';
}

// Currency Converter
async function convertCurrency() {
    const amount = document.getElementById('currency-amount').value;
    const fromCurrency = document.getElementById('currency-from').value;
    const resultDiv = document.getElementById('currency-result');
    
    if (!amount || amount <= 0) {
        showError(resultDiv, 'Введите корректную сумму');
        return;
    }
    
    try {
        showLoading(resultDiv);
        
        const response = await fetch('/api/currency', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount: parseFloat(amount),
                from_currency: fromCurrency
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="success">
                    <strong>💱 Конвертация валют:</strong><br>
                    <div style="font-size: 1.5rem; font-weight: bold; margin: 10px 0;">
                        ${data.amount} ${data.from_currency} = ${data.result.toFixed(2)} ${data.to_currency}
                    </div>
                    <div style="color: #666;">
                        Курс: 1 ${data.from_currency} = ${data.rate} ${data.to_currency}
                    </div>
                </div>
            `;
        } else {
            showError(resultDiv, data.error);
        }
    } catch (error) {
        showError(resultDiv, 'Ошибка при конвертации валют');
    }
}

// Code Generator
async function generateCode() {
    const language = document.getElementById('code-language').value;
    const description = document.getElementById('code-description').value.trim();
    const resultDiv = document.getElementById('code-result');
    
    if (!description) {
        showError(resultDiv, 'Введите описание функции');
        return;
    }
    
    try {
        showLoading(resultDiv);
        
        const response = await fetch('/api/code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                language: language,
                description: description
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="success">
                    <strong>💻 Сгенерированный код (${data.language}):</strong><br>
                    <pre>${data.code}</pre>
                    <button class="copy-btn" onclick="copyToClipboard(\`${data.code.replace(/`/g, '\\`')}\`)">
                        <i class="fas fa-copy"></i> Копировать код
                    </button>
                </div>
            `;
        } else {
            showError(resultDiv, data.error);
        }
    } catch (error) {
        showError(resultDiv, 'Ошибка при генерации кода');
    }
}

// Guess Number Game
async function makeGuess() {
    const guessInput = document.getElementById('guess-input');
    const guess = parseInt(guessInput.value);
    const infoDiv = document.getElementById('guess-info');
    const resultDiv = document.getElementById('guess-result');
    
    if (!guess || guess < 1 || guess > 100) {
        showError(resultDiv, 'Введите число от 1 до 100');
        return;
    }
    
    try {
        const response = await fetch('/api/game/guess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                guess: guess,
                session_id: currentGameSession
            })
        });
        
        const data = await response.json();
        
        if (data.game_started) {
            currentGameSession = data.session_id;
            infoDiv.innerHTML = `<div class="success">${data.message}</div>`;
            resultDiv.innerHTML = '';
            guessInput.value = '';
            return;
        }
        
        if (data.won) {
            infoDiv.innerHTML = `<div class="success">🎉 ${data.message}</div>`;
            resultDiv.innerHTML = `
                <div class="success">
                    <strong>🏆 Поздравляем!</strong><br>
                    Вы угадали число за ${data.attempts} попыток!<br>
                    Получено очков: ${data.score}
                </div>
            `;
            currentGameSession = null;
        } else {
            infoDiv.innerHTML = `<div class="error">${data.message}</div>`;
            resultDiv.innerHTML = `
                <div class="error">
                    Попытка ${data.attempts}. Попробуйте еще раз!
                </div>
            `;
        }
        
        guessInput.value = '';
    } catch (error) {
        showError(resultDiv, 'Ошибка в игре');
    }
}

// Quiz Game
async function startQuiz() {
    const questionDiv = document.getElementById('quiz-question');
    const optionsDiv = document.getElementById('quiz-options');
    const resultDiv = document.getElementById('quiz-result');
    const startBtn = document.getElementById('quiz-start-btn');
    
    try {
        showLoading(questionDiv);
        
        const response = await fetch('/api/quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        currentQuiz = data;
        
        questionDiv.innerHTML = `<strong>❓ ${data.question}</strong>`;
        
        optionsDiv.innerHTML = '';
        data.options.forEach((option, index) => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'quiz-option';
            optionDiv.textContent = `${index + 1}. ${option}`;
            optionDiv.onclick = () => selectQuizOption(index);
            optionsDiv.appendChild(optionDiv);
        });
        
        startBtn.style.display = 'none';
        resultDiv.innerHTML = '';
        
    } catch (error) {
        showError(resultDiv, 'Ошибка при загрузке викторины');
    }
}

function selectQuizOption(selectedIndex) {
    const options = document.querySelectorAll('.quiz-option');
    const resultDiv = document.getElementById('quiz-result');
    
    // Remove previous selections
    options.forEach(option => option.classList.remove('selected'));
    
    // Highlight selected option
    options[selectedIndex].classList.add('selected');
    
    // Check answer
    checkQuizAnswer(selectedIndex);
}

async function checkQuizAnswer(selectedIndex) {
    const resultDiv = document.getElementById('quiz-result');
    
    try {
        const response = await fetch('/api/quiz/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                answer: selectedIndex,
                correct_answer: currentQuiz.correct
            })
        });
        
        const data = await response.json();
        
        if (data.correct) {
            resultDiv.innerHTML = `
                <div class="success">
                    ✅ ${data.message}<br>
                    Получено очков: ${data.score}
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="error">
                    ❌ ${data.message}<br>
                    Правильный ответ: ${currentQuiz.options[currentQuiz.correct]}
                </div>
            `;
        }
        
        // Show start button again
        document.getElementById('quiz-start-btn').style.display = 'inline-flex';
        
    } catch (error) {
        showError(resultDiv, 'Ошибка при проверке ответа');
    }
}

// Utility Functions
function showLoading(element) {
    element.innerHTML = '<div class="loading"></div> Загрузка...';
}

function showError(element, message) {
    element.innerHTML = `<div class="error">❌ ${message}</div>`;
}

function showSuccess(element, message) {
    element.innerHTML = `<div class="success">✅ ${message}</div>`;
}

async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Скопировано в буфер обмена!', 'success');
    } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Скопировано в буфер обмена!', 'success');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize guess game on page load
document.addEventListener('DOMContentLoaded', function() {
    // Start guess game automatically
    fetch('/api/game/guess', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.game_started) {
            currentGameSession = data.session_id;
            document.getElementById('guess-info').innerHTML = `<div class="success">${data.message}</div>`;
        }
    })
    .catch(error => {
        console.log('Guess game initialization failed:', error);
    });
});
