import re
import sys
import time
import random
from bs4 import BeautifulSoup

sys.path.append(r"c:\rpa\Python")

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conexaoBancoPG import ConexaoBancoPG
from matchingProdutos import MatchProdutos
from Classes.Firefox.Firefox.conectaFirefox import FirefoxSeleniumManager
from Classes.GoogleSheets.GoogleSheets.GoogleSheets import GoogleSheets



def normaliza_dados(nome, preco, preco_anterior, desconto, classificacao, tipo_frete, url):
    """
    Normaliza os dados extraídos do Mercado Livre para inserção no banco
    """
    
    # Normaliza o nome (remove espaços extras)
    nome_normalizado = ' '.join(nome.split())
    
    # Normaliza o preço (remove R$ e converte vírgula para ponto)
    preco_normalizado = 0.0
    if preco and preco != "Preço não encontrado":
        preco_limpo = preco.replace('R$', '').replace('.', '').replace(',', '.').strip()
        try:
            preco_normalizado = float(preco_limpo)
        except:
            preco_normalizado = 0.0
    
    # Normaliza o preço anterior
    preco_anterior_normalizado = 0.0
    if preco_anterior and "Preço não encontrado" not in preco_anterior:
        # Usa regex para extrair o valor do aria-label
        match = re.search(r'(\d+)\s+reais?\s+com\s+(\d+)\s+centavos?', preco_anterior)
        if match:
            reais = match.group(1)
            centavos = match.group(2)
            preco_anterior_normalizado = float(f"{reais}.{centavos}")
        else:
            # Tenta extrair direto se vier em outro formato
            preco_limpo = preco_anterior.replace('R$', '').replace('Antes:', '').replace('.', '').replace(',', '.').strip()
            try:
                preco_anterior_normalizado = float(preco_limpo)
            except:
                preco_anterior_normalizado = 0.0
    
    # Normaliza o desconto
    desconto_normalizado = 0.0
    if desconto and "Desconto não encontrado" not in desconto:
        desconto_limpo = desconto.replace('%', '').replace('OFF', '').strip()
        try:
            desconto_normalizado = float(desconto_limpo)
        except:
            desconto_normalizado = 0.0
    
    # Normaliza a classificação (extrai a nota)
    nota = 0.0
    if classificacao and classificacao not in [',', 'Classificação não encontrada']:
        nota_match = re.search(r'Classificação (\d+\.?\d*) de', classificacao)
        if nota_match:
            nota = float(nota_match.group(1))
    
    # Normaliza a quantidade vendida
    quantidade_vendida = 0
    if classificacao and classificacao not in [',', 'Classificação não encontrada']:
        vendas_match = re.search(r'Mais de ([\d]+)(mil)?\s+produtos? vendidos?', classificacao)
        if vendas_match:
            numero = int(vendas_match.group(1))
            if vendas_match.group(2):  # Se tem 'mil'
                quantidade_vendida = numero * 1000
            else:
                quantidade_vendida = numero
    
    # Normaliza o tipo de frete
    tipo_frete_normalizado = tipo_frete if tipo_frete else "Frete comum"
    
    # URL já vem normalizada
    url_normalizada = url
    
    return {
        'nome': nome_normalizado,
        'preco': preco_normalizado,
        'preco_anterior': preco_anterior_normalizado,
        'desconto': desconto_normalizado,
        'classificacao': nota,
        'quantidade_vendida': quantidade_vendida,
        'tipo_frete': tipo_frete_normalizado,
        'url': url_normalizada
    }


def obtem_dados_sheets():
    """
    Obtém os dados da Google Sheets para comparação
    """
    # Exemplo de como obter dados da Google Sheets
    # Substitua 'SUA_PLANILHA_ID' e 'SUA_ABA' pelos valores corretos
    planilha_id = "17sJspSGIatiN3GU8X8oT2UAz6VlwmLz6ha-WtnZAhaY"
    range_dados = "Produtos Top ML!A2:A"
    
    google_sheets = GoogleSheets(id_planilha=planilha_id, range_dados=range_dados, diretorio_json=r"C:\rpa\Python\Analise Itens Mercado Livre\token.json")
    dados_sheets = google_sheets.solicita_tabela()
    
    print(f"Dados obtidos da Google Sheets: {len(dados_sheets)} linhas")
    
    return dados_sheets


def digitar_como_humano(elemento, texto):
    """Digita texto imitando comportamento humano"""
    
    # Limpa o campo primeiro
    elemento.clear()
    time.sleep(random.uniform(0.3, 0.7))
    
    # Digita caractere por caractere com intervalos variados
    for caractere in texto:
        elemento.send_keys(caractere)
        # Intervalo aleatório entre teclas (50ms a 200ms)
        time.sleep(random.uniform(0.05, 0.2))


# ========== CARREGA OS PRODUTOS DE BUSCA DA GOOGLE SHEETS ==========
dados_sheets = obtem_dados_sheets()

# ========== INICIALIZA O MATCHER E CARREGA OS PRODUTOS DA COMPANY_NAME ==========
print("Carregando produtos da COMPANY_NAME...")
matcher = MatchProdutos()
matcher.carrega_produtos_COMPANY_NAME()
print("Produtos carregados!\n")


url = f"https://www.mercadolivre.com.br/"

firefox = FirefoxSeleniumManager()
navegador, chrome_pids = firefox.acessa_navegador()

for produto in dados_sheets:
    navegador.get(url)

    # Espera carregar o elemento de consulta
    WebDriverWait(navegador, 20).until(EC.presence_of_element_located((By.XPATH, f"/html/body/header/div/div[2]/form/input")))
    elemento_consulta = navegador.find_element(By.XPATH, f"/html/body/header/div/div[2]/form/input")
    # time.sleep(random.uniform(1, 3))  # Pausa aleatória para simular comportamento humano
    # elemento_consulta.send_keys("LOCAO HIDRATANTE CETAPHIL RESTORADERM PARA ROSTO E CORPO PELE MUITO SECA 295 ML 1UNID")
    # elemento_consulta.send_keys(str(produto[0]).strip())
    digitar_como_humano(elemento_consulta, str(produto[0]).strip())

    time.sleep(random.uniform(0.5, 1.2))  # Pausa aleatória para simular comportamento humano

    # Espera carregar o elemento de pesquisar
    elemento_consulta.send_keys(Keys.ENTER)

    print("Pesquisa realizada. Aguardando resultados...")

    # Espera o primeiro produto carregar
    WebDriverWait(navegador, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/main/div/div[1]/section/ol/li[1]/div/div")))

    print("Resultados carregados!")

    # Pega o HTML completo da página
    html_completo = navegador.page_source

    # Cria o objeto BeautifulSoup
    soup = BeautifulSoup(html_completo, 'html.parser')

    print("HTML da página capturado e processado com BeautifulSoup.")

    # Agora você pode extrair os dados com BeautifulSoup
    # Exemplo: encontrar todos os produtos
    produtos = soup.find_all('li', class_='ui-search-layout__item')

    print(f"\nTotal de produtos encontrados: {len(produtos)}")

    # Exemplo de extração de dados básicos
    for i, produto in enumerate(produtos):
        try:
            # Título do produto
            titulo = produto.find('h3', class_='poly-component__title-wrapper')
            nome = titulo.text.strip() if titulo else "Título não encontrado"
            
            # Preço
            preco_elem = produto.find('span', class_='andes-money-amount andes-money-amount--cents-superscript')
            preco = preco_elem.text.strip() if preco_elem else "Preço não encontrado"

            # Preço Anterior (se houver)
            preco_ant_elem = produto.find('span', class_='andes-money-amount andes-money-amount--previous andes-money-amount--cents-comma')
            preco_anterior = preco_ant_elem.get('aria-label') if preco_ant_elem else "Preço não encontrado"

            # Desconto (se houver)
            desc_elem = produto.find('span', class_='poly-price__disc_label andes-money-amount__discount poly-price__disc_label--pill')
            desconto = desc_elem.text.strip() if desc_elem else "Desconto não encontrado"

            # Classificação do produto (se houver)
            class_elem = produto.find('span', class_='andes-visually-hidden')
            classificacao = class_elem.text.strip() if class_elem else "Classificação não encontrada"

            # Verifica se é FULL
            tp_frete_elem = produto.find('svg', class_='poly-shipping__promise-icon--full')
            tp_frete = tp_frete_elem.get('aria-label') if tp_frete_elem else "Frete comum"
            
            # Link do produto
            link = produto.find('a', class_='poly-component__title')
            url_produto = link['href'] if link else "Link não encontrado"
            
            print(f"\n--- Produto {i} ---")
            print(f"Nome: {nome}")
            print(f"Preço: {preco}")
            print(f"Preço Anterior: {preco_anterior}")
            print(f"Desconto: {desconto}")
            print(f"Classificação do produto: {classificacao}")
            print(f"Tipo de frete: {tp_frete}")
            print(f"URL: {url_produto}")

            # ========== BUSCA O PRODUTO NA COMPANY_NAME ==========
            matches = matcher.busca_produto_similar(nome, limite_score=70)
            
            codigo_mercadoria = 0
            ean_mercadoria = 0
            
            if matches:
                # Pega o melhor match (primeiro da lista)
                melhor_match = matches[0]
                codigo_mercadoria = melhor_match['codigo']
                ean_mercadoria = melhor_match['ean'] if melhor_match['ean'] else 0
                
                print(f"\n✓ Produto encontrado na COMPANY_NAME (Score: {melhor_match['score']}%)")
                print(f"  Código: {codigo_mercadoria}")
                print(f"  EAN: {ean_mercadoria}")
                print(f"  Descrição COMPANY_NAME: {melhor_match['descricao']}")
            else:
                print(f"\n✗ Produto NÃO encontrado na COMPANY_NAME - usando código 0 e EAN 0")

            # Normaliza os dados
            dados_normalizados = normaliza_dados(
                nome=str(nome).replace("'", "").strip(),
                preco=preco,
                preco_anterior=preco_anterior,
                desconto=desconto,
                classificacao=classificacao,
                tipo_frete=tp_frete,
                url=url_produto
            )
            
            # Insere no banco
            ConexaoBancoPG().insere_dados_pg(
                codigo_mercadoria=codigo_mercadoria,
                ean_mercadoria=ean_mercadoria,
                dados_normalizados=dados_normalizados
            )
            
            print(f"Produto {i} inserido com sucesso!")

        except Exception as e:
            print(f"Erro ao processar produto {i}: {e}")

    tempo_aleatorio = random.uniform(4, 15)
    print(f"\nAguardando {tempo_aleatorio:.2f} segundos antes de processar o próximo produto...")
    time.sleep(tempo_aleatorio)  # Pausa aleatória para evitar bloqueios


navegador.quit()