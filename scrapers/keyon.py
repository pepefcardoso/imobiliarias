from typing import List
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from interfaces.i_scraper import IScraper
from domain.imovel import Imovel

class KeyOnScraper(IScraper):
    def __init__(self, url: str):
        self.url = url

    def buscar_imoveis(self) -> List[Imovel]:
        print(f"  > Iniciando navegador robô para KeyOn...")
        lista_resultados = []

        chrome_options = Options()
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            driver.get(self.url)
            
            print("    Aguardando o carregamento dos dados (5s)...")
            time.sleep(5) 

            html_final = driver.page_source
            soup = BeautifulSoup(html_final, 'html.parser')

            cards = soup.find_all('div', class_='card')
            
            if not cards:
                print("    Aviso: Ainda não encontrei cards. O site pode ter mudado a estrutura.")

            for card in cards:
                try:
                    titulo_tag = card.find('h2', class_='card-title')
                    titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Sem Título"

                    parent_link = card.find_parent('a')
                    link_relativo = parent_link['href'] if parent_link else "#"
                    link = f"https://www.keyonimoveis.com.br{link_relativo}" if not link_relativo.startswith('http') else link_relativo

                    preco = "Sob Consulta"
                    codigo = None
                    preco_container = card.find('strong', class_='preco-imovel-card')
                    if preco_container:
                        texto = preco_container.get_text(strip=True)
                        if "Código." in texto:
                            partes = texto.split("Código.")
                            preco = partes[0].strip()
                            codigo = partes[1].strip()
                        else:
                            preco = texto

                    bairro = "Não identificado"
                    endereco_tag = card.find('span', class_='card-text')
                    if endereco_tag:
                         bairro = endereco_tag.get_text(strip=True)

                    area = "0"
                    quartos = "0"
                    vagas = "0"
                    banheiros = "0"
                    
                    icones = card.find_all('div', class_='container-icon')
                    for div in icones:
                        texto_icone = div.get_text(strip=True).lower()
                        if 'm²' in texto_icone: area = texto_icone
                        elif 'qto' in texto_icone: quartos = texto_icone.replace('qto', '').strip()
                        elif 'vg' in texto_icone: vagas = texto_icone.replace('vg', '').strip()
                        elif 'ban' in texto_icone: banheiros = texto_icone.replace('ban', '').strip()

                    imovel = Imovel(
                        imobiliaria_origem="KeyOn",
                        codigo=codigo,
                        bairro=bairro,
                        titulo=titulo,
                        area=area,
                        quartos=quartos,
                        banheiros=banheiros,
                        vagas=vagas,
                        link=link,
                        preco=preco
                    )
                    lista_resultados.append(imovel)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"    Erro no Selenium: {e}")
        finally:
            driver.quit()

        print(f"  > Encontrados {len(lista_resultados)} imóveis.")
        return lista_resultados