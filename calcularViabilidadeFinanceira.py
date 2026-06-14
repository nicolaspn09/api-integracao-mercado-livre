import requests
import json
import time

class MotorScoringMercadoLivre:
    def __init__(self, access_token, site_id="MLB"):
        """
        Inicializa o orquestrador do framework de scoring.
        A classe exige o token OAuth 2.0 gerado no portal de desenvolvedores do Mercado Livre.
        """
        self.base_url = "https://api.mercadolibre.com"
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.site_id = site_id

    def _executar_requisicao(self, endpoint, params=None):
        """
        Gere as requisições RESTful para a plataforma garantindo captura
        e log em falhas sistêmicas ou expiração de token.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as error:
            print(f"Falha de comunicação com a API em {endpoint}: {error}")
            return None
        except Exception as error:
            print(f"Erro sistêmico imprevisto em {endpoint}: {error}")
            return None

    def extrair_metadados_competitivos(self, termo_pesquisa):
        """
        Analisa a primeira página orgânica de resultados da plataforma para destilar
        volume de mercado, precificação dominante e identificação de atores chave.
        """
        endpoint = f"/sites/{self.site_id}/search"
        parametros = {"q": termo_pesquisa, "limit": 50}
        
        dados_busca = self._executar_requisicao(endpoint, parametros)
        if not dados_busca or not dados_busca.get('results'):
            return None

        resultados = dados_busca['results']
        
        volume_total_vendas = 0
        vendas_lideres = 0
        matriz_precos = []
        concorrentes_unicos = set()

        for indice, produto in enumerate(resultados):
            # A extração referencia o histórico de transações vinculadas ao anúncio.
            vendas = produto.get('sold_quantity', 0)
            preco_venda = produto.get('price', 0)
            id_vendedor = produto.get('seller', {}).get('id')
            
            volume_total_vendas += vendas
            matriz_precos.append(preco_venda)
            if id_vendedor:
                concorrentes_unicos.add(str(id_vendedor))
            
            # Isolando a fatia de mercado dos três maiores atores para índice de monopólio.
            if indice < 3:
                vendas_lideres += vendas

        ticket_medio = sum(matriz_precos) / len(matriz_precos) if matriz_precos else 0
        concentracao_mercado = (vendas_lideres / volume_total_vendas) if volume_total_vendas > 0 else 1.0
        
        barreira_status = self._auditar_lideranca_vendedores(list(concorrentes_unicos))
        
        # Amostragem de provas sociais focada nos líderes do mercado.
        ids_lideres = [produto['id'] for produto in resultados[:5]]
        nota_media, volume_resenhas = self._agrupar_provas_sociais(ids_lideres)
        
        # Validação de tráfego latente baseada nos relatórios de tendências do nicho.
        tendencia_validada = self._validar_demanda_organica(termo_pesquisa, resultados.get("category_id"))

        return {
            "fluxo_vendas_amostra": volume_total_vendas,
            "ticket_medio": ticket_medio,
            "indice_monopolio": concentracao_mercado,
            "densidade_medalhas": barreira_status,
            "avaliacao_qualitativa": nota_media,
            "volume_auditoria_social": volume_resenhas,
            "presenca_tendencia": tendencia_validada,
            "id_categoria_matriz": resultados.get("category_id")
        }

    def _auditar_lideranca_vendedores(self, lista_vendedores):
        """
        Mapeia a força imposta pela hierarquia do motor de busca sobre os concorrentes.
        Emprega o recurso Multiget para minimizar o esgotamento de taxa da API.
        """
        if not lista_vendedores:
            return 0.0
            
        # Segmentação das requisições obedecendo a restrição de tamanho do array da API.
        bloco_vendedores = lista_vendedores[:20] 
        parametros_busca = ",".join(bloco_vendedores)
        endpoint = f"/users?ids={parametros_busca}"
        
        dados_vendedores = self._executar_requisicao(endpoint)
        if not dados_vendedores:
            return 0.0

        contagem_lideranca = 0
        universo_valido = 0

        for resposta_usuario in dados_vendedores:
            if resposta_usuario.get('code') == 200:
                corpo_reposta = resposta_usuario.get('body', {})
                perfil_reputacao = corpo_reposta.get('seller_reputation', {})
                status_poder = perfil_reputacao.get('power_seller_status')
                
                # Identifica contas com precedência sistêmica nas páginas de busca.
                if status_poder in ['platinum', 'gold']:
                    contagem_lideranca += 1
                universo_valido += 1

        return (contagem_lideranca / universo_valido) if universo_valido > 0 else 0.0

    def _agrupar_provas_sociais(self, lista_itens):
        """
        Computa o sentimento do consumidor agrupando as resenhas históricas dos ativos mais relevantes.
        """
        somatorio_notas = 0
        somatorio_volume = 0
        
        for identificador in lista_itens:
            endpoint = f"/reviews/item/{identificador}"
            dados_resenha = self._executar_requisicao(endpoint)
            
            if dados_resenha and 'rating_average' in dados_resenha:
                media = dados_resenha.get('rating_average', 0)
                volumetria = dados_resenha.get('paging', {}).get('total', 0)
                
                somatorio_notas += (media * volumetria)
                somatorio_volume += volumetria
                
            # Interrupção processual obrigatória para impedir bloqueios temporários dos servidores.
            time.sleep(0.15)
            
        nota_equilibrada = (somatorio_notas / somatorio_volume) if somatorio_volume > 0 else 0
        return nota_equilibrada, somatorio_volume

    def _validar_demanda_organica(self, palavra_chave, id_categoria):
        """
        Verifica a tração de pesquisa orgânica através do endpoint oficial de tendências da plataforma.
        """
        if not id_categoria:
            endpoint = f"/trends/{self.site_id}"
        else:
            endpoint = f"/trends/{self.site_id}/{id_categoria}"
            
        dados_tendencias = self._executar_requisicao(endpoint)
        if not dados_tendencias:
            return False
            
        # O processamento examina o array de crescimento e popularidade em busca de validação.
        for tendencia in dados_tendencias:
            termo_trend = tendencia.get('keyword', '').lower()
            if termo_trend in palavra_chave.lower() or palavra_chave.lower() in termo_trend:
                return True
        return False

    def calcular_margem_lucratividade(self, preco_projeto, custo_fornecedor, id_categoria):
        """
        Simula a sobrevivência financeira do negócio descontando a estrutura tarifária exata.
        """
        endpoint = f"/sites/{self.site_id}/listing_prices"
        parametros = {
            "price": preco_projeto,
            "category_id": id_categoria,
            "listing_type_id": "gold_pro" # O modelo projeta inserções de alta tração (Anúncios Premium)
        }
        
        dados_tarifas = self._executar_requisicao(endpoint, parametros)
        custo_plataforma = 0
        
        if dados_tarifas and isinstance(dados_tarifas, list):
            for tarifa in dados_tarifas:
                if tarifa.get('listing_type_id') == 'gold_pro':
                    custo_plataforma = tarifa.get('sale_fee_amount', 0)
                    break
        elif dados_tarifas and isinstance(dados_tarifas, dict):
            custo_plataforma = dados_tarifas.get('sale_fee_amount', 0)
            
        if preco_projeto > 0:
            margem_liquida = (preco_projeto - custo_fornecedor - custo_plataforma) / preco_projeto
            return margem_liquida, custo_plataforma
        return 0, 0

    def rodar_scoring_matematico(self, nomenclatura_produto, custo_erp, projecao_vendas=1500):
        """
        Unifica todas as requisições algorítmicas, enquadra os resultados nas matrizes do 
        framework e sintetiza a inteligência competitiva no Score Ouro, Prata, Bronze ou Rejeição.
        """
        print(f"Sintetizando inteligência de viabilidade para: {nomenclatura_produto}...")
        metricas = self.extrair_metadados_competitivos(nomenclatura_produto)
        
        if not metricas:
            return {"status_execucao": "Falha na modelagem de dados transacionais."}

        # Matriz 1: Liquidez (12%)
        rotatividade = projecao_vendas 
        if rotatividade >= 5000: p_vendas = 100
        elif rotatividade >= 1000: p_vendas = 85
        elif rotatividade >= 500: p_vendas = 70
        elif rotatividade >= 100: p_vendas = 50
        elif rotatividade >= 50: p_vendas = 30
        else: p_vendas = 10
        
        # Matriz 1.2: Intenção Orgânica (8%)
        p_buscas = 100 if metricas['presenca_tendencia'] else 50

        # Matriz 2: Solvência Financeira (10%)
        margem, custo_fixo = self.calcular_margem_lucratividade(metricas['ticket_medio'], custo_erp, metricas['id_categoria_matriz'])
        margem_percentual = margem * 100
        if margem_percentual >= 50: p_margem = 100
        elif margem_percentual >= 40: p_margem = 90
        elif margem_percentual >= 30: p_margem = 75
        elif margem_percentual >= 25: p_margem = 55
        elif margem_percentual >= 20: p_margem = 30
        else: p_margem = 0

        # Matriz 3: Aspereza Competitiva (8%)
        monopolizacao_relativa = metricas['indice_monopolio'] * 100
        if monopolizacao_relativa < 10: p_monopolio = 100
        elif monopolizacao_relativa <= 20: p_monopolio = 80
        elif monopolizacao_relativa <= 30: p_monopolio = 60
        elif monopolizacao_relativa <= 50: p_monopolio = 35
        else: p_monopolio = 10

        # Matriz 3.2: Barreira Algorítmica (6%)
        densidade_lideres = metricas['densidade_medalhas'] * 100
        if densidade_lideres < 15: p_barreira = 100
        elif densidade_lideres <= 30: p_barreira = 75
        elif densidade_lideres <= 50: p_barreira = 50
        else: p_barreira = 25

        # Matriz 2.2: Racionalidade de Empacotamento (6%)
        fator_ticket = metricas['ticket_medio']
        if 100 <= fator_ticket <= 300: p_ticket = 100
        elif 80 <= fator_ticket <= 99: p_ticket = 85
        elif 50 <= fator_ticket <= 79: p_ticket = 70
        elif 300 < fator_ticket <= 500: p_ticket = 60
        elif 30 <= fator_ticket <= 49: p_ticket = 45
        elif fator_ticket > 500: p_ticket = 40
        else: p_ticket = 20

        # Matriz 4: Credibilidade Sistêmica (7%)
        fator_nota = metricas['avaliacao_qualitativa']
        if 4.5 <= fator_nota <= 4.7: p_nota = 100
        elif 4.0 <= fator_nota <= 4.4: p_nota = 85
        elif 4.8 <= fator_nota <= 4.9: p_nota = 70
        elif fator_nota == 5.0: p_nota = 50
        else: p_nota = 30
        
        # Matriz 4.2: Volume de Prova Social (5%)
        volume_soc = metricas['volume_auditoria_social']
        if volume_soc > 500000: p_prova = 100
        elif volume_soc >= 100000: p_prova = 90
        elif volume_soc >= 50000: p_prova = 75
        elif volume_soc >= 10000: p_prova = 60
        else: p_prova = 40

        # Agregação do peso do Produto Mínimo Viável (Base 62%)
        peso_acumulado_mvp = 0.12 + 0.10 + 0.08 + 0.08 + 0.07 + 0.06 + 0.06 + 0.05
        
        pontuacao_liquida = (
            (p_vendas * 0.12) +
            (p_margem * 0.10) +
            (p_monopolio * 0.08) +
            (p_buscas * 0.08) +
            (p_nota * 0.07) +
            (p_barreira * 0.06) +
            (p_ticket * 0.06) +
            (p_prova * 0.05)
        )
        
        resultado_final = round((pontuacao_liquida / peso_acumulado_mvp), 2)

        if resultado_final >= 80: recomendacao_tesouraria = "🟢 OURO (Entrar imediatamente)"
        elif resultado_final >= 60: recomendacao_tesouraria = "🟡 PRATA (Potencial com validação)"
        elif resultado_final >= 40: recomendacao_tesouraria = "🟠 BRONZE (Risco moderado)"
        else: recomendacao_tesouraria = "🔴 REJEITAR (Evitar)"

        return {
            "Identidade do Ativo": nomenclatura_produto,
            "Índice de Viabilidade Estratégica": resultado_final,
            "Diretriz de Execução": recomendacao_tesouraria,
            "Diagnóstico Matemático": {
                "Preço Médio Praticado": f"R$ {fator_ticket:.2f}",
                "Rentabilidade Base Projetada": f"{margem_percentual:.1f}%",
                "Monopolização do Top 3": f"{monopolizacao_relativa:.1f}%",
                "Densidade de Liderança (Medalhas)": f"{densidade_lideres:.1f}%",
                "Nota de Excelência": f"{fator_nota:.2f}★"
            }
        }

# ==========================================
# Implementação Simulada de Varredura
# ==========================================
if __name__ == "__main__":
    # O token deve ser renovado ciclicamente obedecendo a arquitetura de expiração OAuth 2.0.
    CHAVE_ACESSO = "APP_USR-5217101671374903-022014-caee79dc2ff5cd0c09b5d752930ebc6a-19386109" 
    
    orquestrador = MotorScoringMercadoLivre(access_token=CHAVE_ACESSO)
    
    # Processamento iterativo para um ativo hipotético de Dermocosméticos.
    # A variável custo_erp seria alimentada dinamicamente pelas APIs internas do atacadista.
    relatorio_decisao = orquestrador.rodar_scoring_matematico("Sérum Facial Ácido Hialurônico", custo_erp=42.50)
    
    print(json.dumps(relatorio_decisao, indent=4, ensure_ascii=False))