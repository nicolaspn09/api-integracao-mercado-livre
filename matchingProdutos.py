import re
import sys
from rapidfuzz import fuzz, process
import unicodedata

sys.path.append(r"c:\rpa\Python")

from Classes.Oracle.Oracle.ConectaOracle import ConectaOracle


class MatchProdutos:
    def __init__(self):
        self.produtos_COMPANY_NAME = []  # Lista de dicionários com dados da COMPANY_NAME

        
    def normaliza_texto(self, texto):
        """
        Normaliza o texto para melhorar o matching
        """
        if not texto:
            return ""
        
        # Remove acentos
        texto = unicodedata.normalize('NFKD', texto)
        texto = texto.encode('ASCII', 'ignore').decode('ASCII')
        texto = texto.upper()
        
        # Remove pontuações e caracteres especiais
        texto = re.sub(r'[^\w\s]', ' ', texto)
        
        # Remove múltiplos espaços
        texto = ' '.join(texto.split())
        
        # Remove palavras muito comuns que não ajudam no match
        stop_words = ['UNIDADE', 'UNID', 'UN', 'PC', 'PECA', 'KIT', 'C/', 'COM']
        palavras = texto.split()
        palavras = [p for p in palavras if p not in stop_words]
        
        return ' '.join(palavras)

    
    def carrega_produtos_COMPANY_NAME(self):
        """
        Carrega todos os produtos da COMPANY_NAME em memória
        """
        sql = "SELECT CD_MERCADORIA||NR_DV_MERCADORIA, CD_EAN_VENDA, DS_MERCADORIA FROM PRDDM.DC_MERCADORIA WHERE ID_SITUACAO_MERCADORIA = 'A'"

        resultado = ConectaOracle(sql=sql).conecta_oracle()

        for codigo, ean, descricao in resultado:
            self.produtos_COMPANY_NAME.append({
                'codigo': codigo,
                'descricao': descricao,
                'ean': ean,
                'descricao_normalizada': self.normaliza_texto(descricao)
            })

        print(f"Total de produtos carregados da COMPANY_NAME: {len(self.produtos_COMPANY_NAME)}")
        return self.produtos_COMPANY_NAME

    
    def busca_produto_similar(self, nome_mercado_livre, limite_score=70):
        """
        Busca o produto mais similar na base da COMPANY_NAME
        
        Args:
            nome_mercado_livre: Nome do produto vindo do Mercado Livre
            limite_score: Score mínimo para considerar um match (0-100)
        
        Returns:
            Dicionário com os dados do produto ou None
        """
        nome_normalizado = self.normaliza_texto(nome_mercado_livre)
        
        # Extrai apenas as descrições normalizadas para busca
        descricoes = [p['descricao_normalizada'] for p in self.produtos_COMPANY_NAME]
        
        # Busca os 3 melhores matches usando Token Set Ratio
        # (ignora ordem das palavras e palavras duplicadas)
        matches = process.extract(
            nome_normalizado,
            descricoes,
            scorer=fuzz.token_set_ratio,
            limit=3
        )
        
        resultados = []
        for match_texto, score, idx in matches:
            if score >= limite_score:
                produto = self.produtos_COMPANY_NAME[idx]
                resultados.append({
                    'codigo': produto['codigo'],
                    'descricao': produto['descricao'],
                    'ean': produto['ean'],
                    'score': score,
                    'nome_mercado_livre': nome_mercado_livre
                })
        
        return resultados

    
    def processar_lista_mercado_livre(self, nomes_mercado_livre, limite_score=70):
        """
        Processa uma lista de nomes do Mercado Livre
        """
        resultados_todos = []
        
        for nome_ml in nomes_mercado_livre:
            matches = self.busca_produto_similar(nome_ml, limite_score)
            
            if matches:
                # Pega o melhor match (primeiro da lista)
                melhor_match = matches[0]
                resultados_todos.append(melhor_match)
                
                print(f"\n✓ Match encontrado (Score: {melhor_match['score']}%)")
                print(f"  Mercado Livre: {nome_ml}")
                print(f"  COMPANY_NAME: {melhor_match['descricao']}")
                print(f"  Código: {melhor_match['codigo']}")
            else:
                print(f"\n✗ Nenhum match encontrado para: {nome_ml}")
                resultados_todos.append({
                    'codigo': None,
                    'descricao': None,
                    'ean': None,
                    'score': 0,
                    'nome_mercado_livre': nome_ml
                })
        
        return resultados_todos