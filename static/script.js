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

// exibe os resultados na interface
function displayResults(result) {
    const resultsDiv = document.getElementById('resultsSection');
    
    // limpa resultados anteriores
    resultsDiv.innerHTML = '';
    
    // mostra a seção de resultados
    resultsDiv.style.display = 'block';
    
    // debug: log do resultado completo
    console.log('Resultado completo recebido:', result);
    console.log('content_creator_result existe?', !!result.content_creator_result);
    
    // mostra informações do brief
    if (result.brief) {
        const briefCard = document.createElement('div');
        briefCard.className = 'result-card';
        briefCard.innerHTML = `
            <h3>📋 Brief Processado</h3>
            <div class="result-content">
                <p><strong>Tópico:</strong> ${result.brief.topic}</p>
                <p><strong>Público-alvo:</strong> ${result.brief.target_audience}</p>
                <p><strong>Tom:</strong> ${result.brief.tonality}</p>
                <p><strong>Plataformas:</strong> ${result.brief.platforms.join(', ')}</p>
                ${result.brief.additional_info ? `<p><strong>Informações adicionais:</strong> ${result.brief.additional_info}</p>` : ''}
            </div>
        `;
        resultsDiv.appendChild(briefCard);
    }
    
    // resultados do copywriter
    if (result.copywriter_result) {
        const copyCard = document.createElement('div');
        copyCard.className = 'result-card';
        copyCard.innerHTML = `
            <h3>✍️ Copywriter</h3>
            <div class="result-content">
                <h4>Script Principal:</h4>
                <p><strong>Plataforma:</strong> ${result.copywriter_result.scripts[0].platform}</p>
                <p><strong>Script:</strong> ${result.copywriter_result.scripts[0].script}</p>
                <p><strong>Hook:</strong> ${result.copywriter_result.scripts[0].hook}</p>
                <p><strong>CTA:</strong> ${result.copywriter_result.scripts[0].cta}</p>
                <p><strong>Hashtags:</strong> ${result.copywriter_result.hashtags.join(' ')}</p>
                <p><strong>Cronograma:</strong> ${result.copywriter_result.posting_schedule}</p>
            </div>
        `;
        resultsDiv.appendChild(copyCard);
    }
    
    // resultados do editor
    if (result.editor_result) {
        const editorCard = document.createElement('div');
        editorCard.className = 'result-card';
        editorCard.innerHTML = `
            <h3>📝 Editor</h3>
            <div class="result-content">
                <h4>Script Final Otimizado:</h4>
                <p>${result.editor_result.final_script}</p>
                <h4>Melhorias Sugeridas:</h4>
                <ul>
                    ${result.editor_result.improvements.map(imp => `<li>${imp}</li>`).join('')}
                </ul>
                <p><strong>Score de Engajamento:</strong> ${result.editor_result.engagement_score}/10</p>
            </div>
        `;
        resultsDiv.appendChild(editorCard);
    }
    
    // resultados de imagens
    if (result.images_result) {
        const imagesCard = document.createElement('div');
        imagesCard.className = 'result-card';
        imagesCard.innerHTML = `
            <h3>🎨 Especialista em Imagens</h3>
            <div class="result-content">
                <h4>Prompts para Geração de Imagens:</h4>
                <ul>
                    ${result.images_result.prompts.map(prompt => `<li>${prompt}</li>`).join('')}
                </ul>
                <h4>Dicas de Composição:</h4>
                <ul>
                    ${result.images_result.composition_tips.map(tip => `<li>${tip}</li>`).join('')}
                </ul>
                <h4>Paleta de Cores:</h4>
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    ${result.images_result.color_palette.map(color => 
                        `<div style="width: 30px; height: 30px; background: ${color}; border-radius: 5px; border: 1px solid #ddd;" title="${color}"></div>`
                    ).join('')}
                </div>
            </div>
        `;
        resultsDiv.appendChild(imagesCard);
    }
    
    // resultados de produção
    if (result.production_result) {
        const productionCard = document.createElement('div');
        productionCard.className = 'result-card';
        productionCard.innerHTML = `
            <h3>🎬 Especialista em Produção</h3>
            <div class="result-content">
                <h4>Planos de Filmagem:</h4>
                <ul>
                    ${result.production_result.filming_plans.map(plan => 
                        `<li><strong>${plan.shot_type}:</strong> ${plan.background} - ${plan.lighting}</li>`
                    ).join('')}
                </ul>
                <h4>Falas do Apresentador:</h4>
                <ul>
                    ${result.production_result.presenter_lines.map(line => `<li>"${line}"</li>`).join('')}
                </ul>
                <p><strong>Ritmo de Edição:</strong> ${result.production_result.editing_rhythm}</p>
            </div>
        `;
        resultsDiv.appendChild(productionCard);
    }
    
    // resultados do criador de conteúdo
    if (result.content_creator_result) {
        const contentCreatorCard = document.createElement('div');
        contentCreatorCard.className = 'result-card';
        contentCreatorCard.innerHTML = `
            <h3>📝 Criador de Conteúdo Completo</h3>
            <div class="result-content">
                <h4>Conteúdo Completo Gerado:</h4>
                ${result.content_creator_result.full_content.map(content => `
                    <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;">
                        <h5>📄 ${content.title}</h5>
                        <p><strong>Tipo:</strong> ${content.type}</p>
                        <p><strong>Plataforma:</strong> ${content.platform}</p>
                        ${content.estimated_reach ? `<p><strong>Alcance Estimado:</strong> ${content.estimated_reach}</p>` : ''}
                        ${content.engagement_prediction ? `<p><strong>Previsão de Engajamento:</strong> ${content.engagement_prediction}</p>` : ''}
                        
                        ${content.content ? `
                            <div style="margin-top: 10px;">
                                <h6>Conteúdo:</h6>
                                <div style="background: white; padding: 10px; border-radius: 5px; white-space: pre-line; font-family: inherit; line-height: 1.5;">
                                    ${content.content}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${content.slides ? `
                            <div style="margin-top: 10px;">
                                <h6>Slides do Carrossel:</h6>
                                <ul>
                                    ${content.slides.map(slide => `<li>${slide}</li>`).join('')}
                                </ul>
                                ${content.design_notes ? `<p><strong>Notas de Design:</strong> ${content.design_notes}</p>` : ''}
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
                
                <h4>Pilares de Conteúdo:</h4>
                <ul>
                    ${result.content_creator_result.content_pillars.map(pilar => `<li>${pilar}</li>`).join('')}
                </ul>
                
                <h4>Calendário de Conteúdo Semanal:</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 10px;">
                    ${Object.entries(result.content_creator_result.content_calendar).map(([dia, conteudo]) => `
                        <div style="background: #e3f2fd; padding: 10px; border-radius: 8px; text-align: center;">
                            <strong>${dia.charAt(0).toUpperCase() + dia.slice(1)}</strong><br>
                            <small>${conteudo}</small>
                        </div>
                    `).join('')}
                </div>
                
                <div style="margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 8px;">
                    <h6>📋 Diretrizes de Tom:</h6>
                    <p>${result.content_creator_result.tone_guidelines}</p>
                </div>
            </div>
        `;
        resultsDiv.appendChild(contentCreatorCard);
    }
    
    // ideias de conteúdo
    if (result.content_ideas) {
        const ideasCard = document.createElement('div');
        ideasCard.className = 'result-card';
        ideasCard.innerHTML = `
            <h3>💡 Ideias de Conteúdo</h3>
            <div class="result-content">
                <h4>Sugestões de Conteúdo:</h4>
                ${result.content_ideas.content_ideas.map(idea => `
                    <div style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px;">
                        <h5>${idea.title}</h5>
                        <p><strong>Conceito:</strong> ${idea.concept}</p>
                        <p><strong>Potencial Viral:</strong> ${(idea.viral_potential * 100).toFixed(0)}%</p>
                        <p><strong>Plataformas:</strong> ${idea.platform_fit.join(', ')}</p>
                    </div>
                `).join('')}
                <h4>Tópicos em Alta:</h4>
                <p>${result.content_ideas.trending_topics.map(topic => `#${topic}`).join(' ')}</p>
            </div>
        `;
        resultsDiv.appendChild(ideasCard);
    }
    
    // adiciona botões de cópia após exibir todos os resultados
    setTimeout(() => {
        addCopyButtons();
    }, 100);
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