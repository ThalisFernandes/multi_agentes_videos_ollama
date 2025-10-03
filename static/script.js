// configuração da API
const API_BASE_URL = 'http://localhost:8000';

// elementos do DOM
const briefForm = document.getElementById('briefForm');
const submitBtn = document.getElementById('submitBtn');
const statusSection = document.getElementById('statusSection');
const resultsSection = document.getElementById('resultsSection');
const briefIdSpan = document.getElementById('briefId');
const briefStatusSpan = document.getElementById('briefStatus');
const loadingSpinner = document.getElementById('loadingSpinner');
const checkStatusBtn = document.getElementById('checkStatusBtn');

// elementos de resultado
const copywriterResult = document.getElementById('copywriterResult');
const editorResult = document.getElementById('editorResult');
const imagesResult = document.getElementById('imagesResult');
const productionResult = document.getElementById('productionResult');
const contentIdeasResult = document.getElementById('contentIdeasResult');

// variável global para armazenar o brief ID atual
let currentBriefId = null;
let statusCheckInterval = null;

// event listeners
briefForm.addEventListener('submit', handleFormSubmit);
checkStatusBtn.addEventListener('click', checkBriefStatus);

// função principal para envio do formulário
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(briefForm);
    const briefData = extractFormData(formData);
    
    try {
        setLoadingState(true);
        const response = await submitBrief(briefData);
        
        if (response.brief_id) {
            currentBriefId = response.brief_id;
            showStatusSection(response);
            startStatusPolling();
        }
    } catch (error) {
        showError('Erro ao enviar brief: ' + error.message);
    } finally {
        setLoadingState(false);
    }
}

// extrai dados do formulário
function extractFormData(formData) {
    const briefData = {};
    
    // campos simples
    briefData.topic = formData.get('topic');
    briefData.duration = parseInt(formData.get('duration')) || 60;
    briefData.tonality = formData.get('tonality');
    briefData.target_audience = formData.get('target_audience');
    briefData.additional_context = formData.get('additional_context');
    
    // plataformas selecionadas
    const platforms = formData.getAll('platforms');
    briefData.platforms = platforms.length > 0 ? platforms : ['tiktok'];
    
    // remove campos vazios
    Object.keys(briefData).forEach(key => {
        if (briefData[key] === '' || briefData[key] === null) {
            delete briefData[key];
        }
    });
    
    return briefData;
}

// envia brief para a API
async function submitBrief(briefData) {
    const response = await fetch(`${API_BASE_URL}/brief`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(briefData)
    });
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
    }
    
    return await response.json();
}

// verifica status do brief
async function checkBriefStatus() {
    if (!currentBriefId) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/brief/${currentBriefId}/status`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        updateStatusDisplay(data);
        
        if (data.status === 'completed' && data.result) {
            displayResults(data.result);
            stopStatusPolling();
        }
    } catch (error) {
        console.error('Erro ao verificar status:', error);
        showError('Erro ao verificar status: ' + error.message);
    }
}

// exibe seção de status
function showStatusSection(response) {
    briefIdSpan.textContent = response.brief_id;
    briefStatusSpan.textContent = response.status;
    briefStatusSpan.className = `status-badge ${response.status}`;
    
    statusSection.style.display = 'block';
    statusSection.classList.add('fade-in');
    
    // scroll suave para a seção de status
    statusSection.scrollIntoView({ behavior: 'smooth' });
}

// atualiza display do status
function updateStatusDisplay(data) {
    briefStatusSpan.textContent = data.status;
    briefStatusSpan.className = `status-badge ${data.status}`;
    
    if (data.status === 'completed') {
        loadingSpinner.style.display = 'none';
    }
}

// exibe resultados
function displayResults(results) {
    // copywriter
    if (results.copywriter_result) {
        copywriterResult.textContent = formatResult(results.copywriter_result);
    }
    
    // editor
    if (results.editor_result) {
        editorResult.textContent = formatResult(results.editor_result);
    }
    
    // images
    if (results.images_result) {
        imagesResult.textContent = formatResult(results.images_result);
    }
    
    // production
    if (results.production_result) {
        productionResult.textContent = formatResult(results.production_result);
    }
    
    // content ideas
    if (results.content_ideas) {
        contentIdeasResult.textContent = formatResult(results.content_ideas);
    }
    
    // mostra seção de resultados
    resultsSection.style.display = 'block';
    resultsSection.classList.add('fade-in');
    
    // scroll suave para os resultados
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }, 300);
}

// formata resultado para exibição
function formatResult(result) {
    if (typeof result === 'string') {
        return result;
    } else if (typeof result === 'object') {
        return JSON.stringify(result, null, 2);
    }
    return String(result);
}

// inicia polling de status
function startStatusPolling() {
    // verifica imediatamente
    setTimeout(checkBriefStatus, 2000);
    
    // depois verifica a cada 5 segundos
    statusCheckInterval = setInterval(checkBriefStatus, 5000);
}

// para polling de status
function stopStatusPolling() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
}

// define estado de loading
function setLoadingState(isLoading) {
    submitBtn.disabled = isLoading;
    
    if (isLoading) {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
        submitBtn.classList.add('loading');
    } else {
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Gerar Conteúdo';
        submitBtn.classList.remove('loading');
    }
}

// exibe erro
function showError(message) {
    // cria elemento de erro se não existir
    let errorDiv = document.getElementById('errorMessage');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'errorMessage';
        errorDiv.style.cssText = `
            background: #fed7d7;
            color: #c53030;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #c53030;
            display: none;
        `;
        briefForm.parentNode.insertBefore(errorDiv, briefForm.nextSibling);
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    errorDiv.classList.add('fade-in');
    
    // remove erro após 5 segundos
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// limpa resultados anteriores
function clearPreviousResults() {
    statusSection.style.display = 'none';
    resultsSection.style.display = 'none';
    
    // limpa conteúdo dos resultados
    copywriterResult.textContent = '';
    editorResult.textContent = '';
    imagesResult.textContent = '';
    productionResult.textContent = '';
    contentIdeasResult.textContent = '';
    
    // para polling anterior
    stopStatusPolling();
    currentBriefId = null;
}

// adiciona listener para limpar resultados quando formulário é modificado
briefForm.addEventListener('input', () => {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
});

// função para copiar resultado para clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // feedback visual de cópia
        const notification = document.createElement('div');
        notification.textContent = 'Copiado para a área de transferência!';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #48bb78;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            z-index: 1000;
            animation: fadeIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 3000);
    }).catch(err => {
        console.error('Erro ao copiar:', err);
    });
}

// adiciona botões de cópia aos resultados quando eles são exibidos
function addCopyButtons() {
    const resultCards = document.querySelectorAll('.result-card');
    
    resultCards.forEach(card => {
        const content = card.querySelector('.result-content');
        if (content && content.textContent.trim() && !content.textContent.includes('Aguardando')) {
            // verifica se já tem botão
            if (!card.querySelector('.copy-btn')) {
                const copyBtn = document.createElement('button');
                copyBtn.className = 'copy-btn';
                copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copiar Resultado';
                copyBtn.style.cssText = `
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 0.95rem;
                    font-weight: 600;
                    margin-top: 15px;
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                `;
                
                copyBtn.addEventListener('click', () => {
                    copyToClipboard(content.textContent);
                });
                
                copyBtn.addEventListener('mouseenter', () => {
                    copyBtn.style.background = '#5a67d8';
                    copyBtn.style.transform = 'translateY(-2px)';
                    copyBtn.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
                });
                
                copyBtn.addEventListener('mouseleave', () => {
                    copyBtn.style.background = '#667eea';
                    copyBtn.style.transform = 'translateY(0)';
                    copyBtn.style.boxShadow = 'none';
                });
                
                card.appendChild(copyBtn);
            }
        }
    });
}

// observer para adicionar botões de cópia quando resultados aparecem
const resultsObserver = new MutationObserver(() => {
    addCopyButtons();
});

resultsObserver.observe(resultsSection, {
    childList: true,
    subtree: true,
    characterData: true
});

// inicialização
document.addEventListener('DOMContentLoaded', () => {
    console.log('Frontend Multi-Agentes Conteúdo carregado!');
    
    // limpa qualquer estado anterior
    clearPreviousResults();
});