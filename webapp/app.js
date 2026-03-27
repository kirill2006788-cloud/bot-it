// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();
tg.enableClosingConfirmation();

// Применяем тему Telegram
document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
document.documentElement.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color || '#2481cc');
document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#2481cc');
document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#f4f4f5');

// Состояние приложения
let chatHistory = [];
let currentProject = null;
let codeEditor = null;
const userId = tg.initDataUnsafe?.user?.id || 'demo';

// API endpoint (измените на ваш сервер)
const API_URL = window.location.origin;

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initChat();
    initCodeEditor();
    initProjects();
    loadChatHistory();
});

// Навигация между вкладками
function initNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const views = document.querySelectorAll('.view');
    
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const viewName = btn.dataset.view;
            
            // Переключаем активные кнопки
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Переключаем виды
            views.forEach(v => v.classList.remove('active'));
            document.getElementById(`${viewName}-view`).classList.add('active');
            
            tg.HapticFeedback.impactOccurred('light');
        });
    });
}

// AI Chat
function initChat() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Добавляем сообщение пользователя
    addMessageToChat('user', message);
    chatInput.value = '';
    
    // Показываем индикатор печати
    showTypingIndicator();
    
    try {
        // Отправляем на сервер
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                message: message,
                init_data: tg.initData
            })
        });
        
        const data = await response.json();
        
        // Убираем индикатор печати
        removeTypingIndicator();
        
        // Добавляем ответ AI
        addMessageToChat('ai', data.response);
        
        // Сохраняем историю
        saveChatHistory();
        
        tg.HapticFeedback.notificationOccurred('success');
    } catch (error) {
        removeTypingIndicator();
        addMessageToChat('ai', '❌ Ошибка соединения. Попробуйте снова.');
        tg.HapticFeedback.notificationOccurred('error');
    }
}

function addMessageToChat(type, text) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Добавляем в историю
    chatHistory.push({ type, text, timestamp: Date.now() });
}

function showTypingIndicator() {
    const messagesDiv = document.getElementById('chatMessages');
    const indicator = document.createElement('div');
    indicator.className = 'message ai typing-indicator';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    messagesDiv.appendChild(indicator);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

function loadChatHistory() {
    const saved = localStorage.getItem(`chat_history_${userId}`);
    if (saved) {
        chatHistory = JSON.parse(saved);
        chatHistory.forEach(msg => {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${msg.type}`;
            messageDiv.textContent = msg.text;
            messagesDiv.appendChild(messageDiv);
        });
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

function saveChatHistory() {
    localStorage.setItem(`chat_history_${userId}`, JSON.stringify(chatHistory));
}

// Code Editor
function initCodeEditor() {
    codeEditor = CodeMirror(document.getElementById('codeEditor'), {
        mode: 'python',
        theme: 'monokai',
        lineNumbers: true,
        lineWrapping: true,
        value: '# Напишите или вставьте код здесь\n\ndef hello_world():\n    print("Hello from Telegram!")\n\nhello_world()'
    });
    
    const languageSelect = document.getElementById('languageSelect');
    const aiHelpBtn = document.getElementById('aiHelpBtn');
    const saveCodeBtn = document.getElementById('saveCodeBtn');
    
    languageSelect.addEventListener('change', (e) => {
        codeEditor.setOption('mode', e.target.value);
        tg.HapticFeedback.impactOccurred('light');
    });
    
    aiHelpBtn.addEventListener('click', getAIHelp);
    saveCodeBtn.addEventListener('click', saveCode);
}

async function getAIHelp() {
    const code = codeEditor.getValue();
    const language = document.getElementById('languageSelect').value;
    
    if (!code.trim()) {
        tg.showAlert('Напишите код сначала!');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_URL}/api/ai-help`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                code: code,
                language: language,
                init_data: tg.initData
            })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        const suggestionsDiv = document.getElementById('aiSuggestions');
        suggestionsDiv.innerHTML = `
            <h3>🤖 AI Предложения:</h3>
            <p>${data.suggestion}</p>
        `;
        
        tg.HapticFeedback.notificationOccurred('success');
    } catch (error) {
        hideLoading();
        tg.showAlert('Ошибка получения помощи AI');
        tg.HapticFeedback.notificationOccurred('error');
    }
}

function saveCode() {
    const code = codeEditor.getValue();
    const language = document.getElementById('languageSelect').value;
    const filename = `code.${language === 'python' ? 'py' : language === 'javascript' ? 'js' : language}`;
    
    // Отправляем код обратно в бот
    tg.sendData(JSON.stringify({
        action: 'save_code',
        filename: filename,
        code: code,
        language: language
    }));
    
    tg.showPopup({
        title: '✅ Сохранено!',
        message: `Файл ${filename} отправлен в чат`,
        buttons: [{type: 'ok'}]
    });
}

// Projects Manager
function initProjects() {
    const createProjectBtn = document.getElementById('createProjectBtn');
    const generateProjectBtn = document.getElementById('generateProjectBtn');
    const cancelProjectBtn = document.getElementById('cancelProjectBtn');
    const projectForm = document.getElementById('projectForm');
    
    createProjectBtn.addEventListener('click', () => {
        projectForm.classList.add('active');
        tg.HapticFeedback.impactOccurred('medium');
    });
    
    cancelProjectBtn.addEventListener('click', () => {
        projectForm.classList.remove('active');
        document.getElementById('projectName').value = '';
        document.getElementById('projectDesc').value = '';
    });
    
    generateProjectBtn.addEventListener('click', generateProject);
    
    loadProjects();
}

async function generateProject() {
    const name = document.getElementById('projectName').value.trim();
    const desc = document.getElementById('projectDesc').value.trim();
    
    if (!name || !desc) {
        tg.showAlert('Заполните все поля!');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_URL}/api/generate-project`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                name: name,
                description: desc,
                init_data: tg.initData
            })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        // Закрываем форму
        document.getElementById('projectForm').classList.remove('active');
        document.getElementById('projectName').value = '';
        document.getElementById('projectDesc').value = '';
        
        // Добавляем проект в список
        addProjectToList(data.project);
        
        tg.showPopup({
            title: '🎉 Проект создан!',
            message: `Проект "${name}" с ${data.files_count} файлами готов!`,
            buttons: [{type: 'ok'}]
        });
        
        tg.HapticFeedback.notificationOccurred('success');
    } catch (error) {
        hideLoading();
        tg.showAlert('Ошибка создания проекта');
        tg.HapticFeedback.notificationOccurred('error');
    }
}

function addProjectToList(project) {
    const projectsList = document.getElementById('projectsList');
    
    // Убираем empty state
    const emptyState = projectsList.querySelector('.empty-state');
    if (emptyState) emptyState.remove();
    
    const card = document.createElement('div');
    card.className = 'project-card';
    card.innerHTML = `
        <h3>📦 ${project.name}</h3>
        <p>${project.description}</p>
        <div class="files-count">📄 Файлов: ${project.files_count}</div>
    `;
    
    card.addEventListener('click', () => {
        downloadProject(project);
    });
    
    projectsList.insertBefore(card, projectsList.firstChild);
    
    // Сохраняем в localStorage
    saveProjects();
}

function downloadProject(project) {
    tg.sendData(JSON.stringify({
        action: 'download_project',
        project_id: project.id
    }));
    
    tg.showPopup({
        title: '📥 Скачивание',
        message: 'Проект отправлен в чат!',
        buttons: [{type: 'ok'}]
    });
}

function loadProjects() {
    const saved = localStorage.getItem(`projects_${userId}`);
    if (saved) {
        const projects = JSON.parse(saved);
        projects.forEach(addProjectToList);
    }
}

function saveProjects() {
    const cards = document.querySelectorAll('.project-card');
    const projects = Array.from(cards).map(card => ({
        name: card.querySelector('h3').textContent.replace('📦 ', ''),
        description: card.querySelector('p').textContent,
        files_count: parseInt(card.querySelector('.files-count').textContent.match(/\d+/)[0]),
        id: Date.now()
    }));
    localStorage.setItem(`projects_${userId}`, JSON.stringify(projects));
}

// Утилиты
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

// Обработка закрытия WebApp
tg.onEvent('popupClosed', () => {
    console.log('Popup closed');
});
