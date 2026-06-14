import requests

def renovar_token_acesso(app_id, secret_key, refresh_token_atual):
    url = "https://api.mercadolibre.com/oauth/token"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }
    
    payload = {
        "grant_type": "refresh_token",
        "client_id": app_id,
        "client_secret": secret_key,
        "refresh_token": refresh_token_atual
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status() 
        
        novos_tokens = response.json()
        
        # OBRIGATÓRIO: Salvar o novos_tokens['access_token'] E o novos_tokens['refresh_token']
        return novos_tokens
        
    except requests.exceptions.RequestException as e:
        print(f"Falha crítica na renovação do token: {e}")
        if e.response is not None:
            print(f"Erro retornado: {e.response.json()}")
        return None

# Uso:
novos_dados = renovar_token_acesso("5217101671374903", "EXF3hSU7zzPnAcnzlxjNPmjChfAbn9oY", "APP_USR-5217101671374903-022014-caee79dc2ff5cd0c09b5d752930ebc6a-19386109")