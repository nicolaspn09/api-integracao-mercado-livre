import sys
from datetime import datetime

sys.path.append(r"c:\rpa\Python")

from Classes.Postgres.Postgres.ConectaPG import ConectaPG


class ConexaoBancoPG():
    def __init__(self):
        pass


    def insere_dados_pg(self, codigo_mercadoria, ean_mercadoria, dados_normalizados):
        """
        Insere dados normalizados no banco PostgreSQL
        """
        sql = f"""INSERT INTO rpa.analise_itens_mercado_livre 
                (codigo_mercadoria, ean_mercadoria, nome_mercadoria, preco_mercado_livre, 
                preco_sem_desconto_mercado_livre, desconto_mercado_livre, classificacao_produto, 
                quantidade_aproximada_vendida, tipo_frete_mercado_livre, url_produto_mercado_livre, 
                data_pesquisa) 
                VALUES({codigo_mercadoria}, {ean_mercadoria}, '{dados_normalizados['nome']}', 
                        {dados_normalizados['preco']}, {dados_normalizados['preco_anterior']}, 
                        {dados_normalizados['desconto']}, {dados_normalizados['classificacao']}, 
                        {dados_normalizados['quantidade_vendida']}, '{dados_normalizados['tipo_frete']}', 
                        '{dados_normalizados['url']}', '{datetime.now()}')"""
        
        ConectaPG(sql=sql).conecta_pg_insert()

    
    def consulta_produtos(self):
        sql = f"SELECT codigo_mercadoria, ean_mercadoria, nome_mercadoria, preco_mercado_livre, preco_sem_desconto_mercado_livre, desconto_mercado_livre, classificacao_produto, quantidade_aproximada_vendida, tipo_frete_mercado_livre, url_produto_mercado_livre, data_pesquisa FROM rpa.analise_itens_mercado_livre"

        ConectaPG(sql=sql).conecta_pg()