import json
import time
from typing import List
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from interfaces.i_scraper import IScraper
from domain.imovel import Imovel

class QualAlugarScraper(IScraper):
    def __init__(self, url: str):
        self.url = url

    def buscar_imoveis(self) -> List[Imovel]:
        print(f"  > Iniciando navegador robô para QualAlugar...")
        lista_resultados = []

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            driver.get(self.url)
            print("    Aguardando carregamento (5s)...")
            time.sleep(5)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            script_data = soup.find('script', id='__NEXT_DATA__')
            
            if script_data:
                json_content = json.loads(script_data.string)
                
                try:
                    lista_imoveis_raw = json_content['props']['pageProps']['imoveis']
                except KeyError:
                    lista_imoveis_raw = []
                    print("    Aviso: Caminho do JSON mudou ou não há imóveis.")

                for item in lista_imoveis_raw:
                    try:
                        titulo = item.get('imv_titulo')
                        if not titulo:
                            continue 
                        
                        codigo = item.get('imv_cod_gaia', '?')
                        bairro = item.get('imv_bairro', '?')
                        link = item.get('url_amiga', '#')
                        
                        valor_num = item.get('imv_preco_locacao')
                        preco = f"R$ {valor_num}" if valor_num else "Consultar"
                        
                        area_num = item.get('imv_area_util')
                        area = f"{area_num} m²" if area_num else "?"
                        
                        quartos = str(item.get('imv_qtd_dorm', '?'))
                        banheiros = str(item.get('imv_qtd_banheiros', '?'))
                        vagas = str(item.get('imv_qtd_vagas', '?'))

                        imovel = Imovel(
                            imobiliaria_origem="QualAlugar",
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

                    except Exception as e_item:
                        continue
            else:
                print("    Erro: Não encontrei os dados estruturados (__NEXT_DATA__).")

        except Exception as e:
            print(f"    Erro no Selenium QualAlugar: {e}")
        finally:
            driver.quit()

        print(f"  > Encontrados {len(lista_resultados)} imóveis na QualAlugar.")
        return lista_resultados