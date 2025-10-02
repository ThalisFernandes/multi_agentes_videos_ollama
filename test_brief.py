import requests
import json
import time

# configuracao da API
BASE_URL = "http://localhost:8000"

def test_brief_workflow():
    """
    Demonstra o fluxo completo de uso da API:
    1. Enviar brief
    2. Consultar status
    3. Obter resultados dos agentes
    """
    
    print("=== TESTE DO FLUXO COMPLETO DE BRIEF ===\n")
    
    # 1. Enviando brief
    print("1. Enviando brief...")
    brief_data = {
        "topic": "Marketing Digital para E-commerce",
        "target_audience": "Empreendedores 25-40 anos",
        "tonality": "profissional mas acessível",
        "platforms": ["instagram", "tiktok", "youtube"]
    }
    
    response = requests.post(f"{BASE_URL}/brief", json=brief_data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    
    brief_id = response.json().get("brief_id")
    print(f"Brief ID gerado: {brief_id}\n")
    
    # 2. Consultando status
    print("2. Consultando status do processamento...")
    status_response = requests.get(f"{BASE_URL}/brief/{brief_id}/status")
    print(f"Status: {status_response.status_code}")
    
    status_data = status_response.json()
    print(f"Status do brief: {status_data['status']}")
    print(f"Progresso: {status_data['progress']}%\n")
    
    # 3. Obtendo resultados completos
    if status_data['status'] == 'completed':
        print("3. Brief processado! Obtendo resultados dos agentes...\n")
        
        result = status_data.get('result', {})
        
        # exibindo resultados por agente
        print("📝 COPYWRITER:")
        copywriter = result.get('copywriter_result', {})
        if copywriter:
            for script in copywriter.get('scripts', []):
                print(f"  Platform: {script['platform']}")
                print(f"  Script: {script['script']}")
                print(f"  Hook: {script['hook']}")
                print(f"  CTA: {script['cta']}")
            print(f"  Hashtags: {copywriter.get('hashtags', [])}")
            print(f"  Cronograma: {copywriter.get('posting_schedule', '')}\n")
        
        print("✏️ EDITOR:")
        editor = result.get('editor_result', {})
        if editor:
            print(f"  Script final: {editor.get('final_script', '')}")
            print(f"  Score de engajamento: {editor.get('engagement_score', 0)}")
            print(f"  Melhorias sugeridas: {editor.get('improvements', [])}\n")
        
        print("🎨 IMAGENS:")
        images = result.get('images_result', {})
        if images:
            print("  Prompts para IA:")
            for prompt in images.get('prompts', []):
                print(f"    - {prompt}")
            print(f"  Paleta de cores: {images.get('color_palette', [])}")
            print(f"  Dicas de composição: {images.get('composition_tips', [])}\n")
        
        print("🎬 PRODUÇÃO:")
        production = result.get('production_result', {})
        if production:
            print("  Planos de filmagem:")
            for plan in production.get('filming_plans', []):
                print(f"    - {plan['shot_type']}: {plan['background']} ({plan['lighting']})")
            print(f"  Ritmo de edição: {production.get('editing_rhythm', '')}")
            print("  Falas do apresentador:")
            for line in production.get('presenter_lines', []):
                print(f"    - \"{line}\"")
            print()
        
        print("💡 IDEIAS DE CONTEÚDO:")
        content_ideas = result.get('content_ideas', {})
        if content_ideas:
            for idea in content_ideas.get('content_ideas', []):
                print(f"  📌 {idea['title']}")
                print(f"     Conceito: {idea['concept']}")
                print(f"     Potencial viral: {idea['viral_potential']}")
                print(f"     Plataformas: {idea['platform_fit']}")
            print(f"  Trending topics: {content_ideas.get('trending_topics', [])}")
    
    else:
        print("Brief ainda processando...")

if __name__ == "__main__":
    test_brief_workflow()