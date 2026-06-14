# import requests

# def analisar_mercado_produto(termo_busca, access_token):
#     # Endpoint de busca do Brasil (MLB)
#     url = f"https://api.mercadolibre.com/products/search?status=active&site_id=MLB&q={termo_busca}"
    
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }
    
#     response = requests.get(url, headers=headers)
    
#     if response.status_code != 200:
#         print(f"Erro na API: {response.status_code} - {response.text}")
#         return None
        
#     dados = response.json()
    
#     total_anuncios = dados.get("paging", {}).get("total", 0)
#     resultados = dados.get("results", [])
    
#     if not resultados:
#         return {"erro": "Nenhum produto encontrado"}

#     metricas = {
#         "termo": termo_busca,
#         "total_concorrentes": total_anuncios,
#         "precos": [],
#         "medalhas_sellers": {"gold": 0, "platinum": 0, "sem_medalha": 0},
#         "produtos_no_full": 0,
#         "top_10_ids": []
#     }
    
#     # Avaliando a primeira página (Top 50 resultados padrão)
#     for idx, item in enumerate(resultados):
#         # Coleta IDs para a fase 2 (Reviews)
#         if idx < 10:
#             metricas["top_10_ids"].append(item["id"])
            
#         # Financeiro: Preços
#         metricas["precos"].append(item["price"])
        
#         # Logística: Compatibilidade Mercado Envios
#         logistic_type = item.get("shipping", {}).get("logistic_type", "")
#         if logistic_type == "fulfillment":
#             metricas["produtos_no_full"] += 1
            
#         # Competitividade: Barreira de Entrada
#         seller_level = item.get("seller", {}).get("seller_reputation", {}).get("level_id", "")
#         if seller_level == "5_green": # No json da busca, gold/platinum vêm como power_seller_status, o level_id é cor
#             power_status = item.get("seller", {}).get("seller_reputation", {}).get("power_seller_status", "")
#             if power_status == "platinum":
#                 metricas["medalhas_sellers"]["platinum"] += 1
#             elif power_status == "gold":
#                 metricas["medalhas_sellers"]["gold"] += 1
#             else:
#                 metricas["medalhas_sellers"]["sem_medalha"] += 1
#         else:
#             metricas["medalhas_sellers"]["sem_medalha"] += 1

#     # Cálculos pós-coleta
#     if metricas["precos"]:
#         metricas["ticket_medio"] = sum(metricas["precos"]) / len(metricas["precos"])
#         metricas["gap_preco"] = {
#             "min": min(metricas["precos"]),
#             "max": max(metricas["precos"])
#         }
        
#     metricas["taxa_full_pagina_1"] = (metricas["produtos_no_full"] / len(resultados)) * 100

#     return metricas


import requests
from collections import Counter

def analisar_mercado_produto(termo_busca, access_token):
    # ROTA CORRETA: Busca os anúncios reais no Brasil (MLB)
    url = f"https://api.mercadolibre.com/products/search?status=active&site_id=MLB&q={termo_busca}"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Erro na API: {response.status_code} - {response.text}")
        return None
        
    dados = response.json()

    # print(dados)
    
    total_anuncios = dados.get("paging", {}).get("total", 0)
    resultados = dados.get("results", [])
    
    if not resultados:
        return {"erro": "Nenhum anúncio encontrado para este termo."}

    metricas = {
        "termo": termo_busca,
        "total_concorrentes": total_anuncios,
        "produtos_no_full": 0,
        "medalhas_sellers": {"platinum": 0, "gold": 0, "sem_medalha": 0},
        "top_10_ids": []
    }
    
    # Avaliando os resultados
    for idx, item in enumerate(resultados):
        if idx < 10:
            metricas["top_10_ids"].append(item["id"])
            
        # Logística: Compatibilidade Mercado Envios Full
        if item.get("shipping", {}).get("logistic_type", "") == "fulfillment":
            metricas["produtos_no_full"] += 1
            
        # Competitividade: Barreira de Entrada (Medalhas)
        power_status = item.get("seller", {}).get("seller_reputation", {}).get("power_seller_status")
        if power_status == "platinum":
            metricas["medalhas_sellers"]["platinum"] += 1
        elif power_status == "gold":
            metricas["medalhas_sellers"]["gold"] += 1
        else:
            metricas["medalhas_sellers"]["sem_medalha"] += 1
            
    metricas["taxa_full_pagina_1"] = (metricas["produtos_no_full"] / len(resultados)) * 100

    return metricas

# Exemplo de uso:
analise = analisar_mercado_produto("CeraVe Loção Hidratante", "APP_USR-5217101671374903-022007-4f82fa56cde5556fa6a72e59784a16b3-19386109")
print(analise)