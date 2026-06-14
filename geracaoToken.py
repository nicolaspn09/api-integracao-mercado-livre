import requests

def obter_token_acesso(app_id, secret_key, auth_code, redirect_uri, code_verifier):
    url = "https://api.mercadolibre.com/oauth/token"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }
    
    payload = {
        "grant_type": "authorization_code",
        "client_id": app_id,
        "client_secret": secret_key,
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status() # Lança exceção se o status HTTP indicar erro (ex: 400, 401)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        if response.text:
            print(f"Detalhes do erro retornado pela API: {response.json()}")
        return None

# Exemplo de uso:
dados_token = obter_token_acesso(
    app_id="5217101671374903",
    secret_key="EXF3hSU7zzPnAcnzlxjNPmjChfAbn9oY",
    auth_code="TG-699f2d284ddf0300015b18d7-19386109",
    redirect_uri="https://www.sigaa.ifsc.edu.br/sigaa/verTelaLogin.do",
    code_verifier="TG-699f2d284ddf0300015b18d7-19386109"
)
print(dados_token)