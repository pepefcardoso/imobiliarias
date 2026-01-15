from bs4 import BeautifulSoup, Tag
from interfaces.i_parser import IParser
from domain.imovel import Imovel
from domain.scraper_result import ScraperResult

class KeyOnParser(IParser):
    def parse(self, html_content: str) -> ScraperResult:
        soup = BeautifulSoup(html_content, 'html.parser')
        cards = soup.find_all('div', class_='card')
        
        resultado = ScraperResult()
        
        for card in cards:
            try:
                imovel = self._processar_card(card)
                resultado.imoveis.append(imovel)
            except Exception as e:
                msg_erro = f"Erro ao processar card: {str(e)}"
                resultado.erros.append(msg_erro)
                
        return resultado

    def _processar_card(self, card: Tag) -> Imovel:
        titulo_tag = card.find('h2', class_='card-title')
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else "?"

        parent_link = card.find_parent('a')
        link_relativo = parent_link['href'] if parent_link else "#"
        link = f"https://www.keyonimoveis.com.br{link_relativo}" if not link_relativo.startswith('http') else link_relativo

        preco = "?"
        preco_container = card.find('strong', class_='preco-imovel-card')
        if preco_container:
            preco = preco_container.get_text(strip=True)

        codigo = "?"
        codigo_tag = card.find('span', class_='preco-cond-card')
        if codigo_tag:
            texto_cod = codigo_tag.get_text(strip=True)
            codigo = texto_cod.replace('Código.', '').strip()

        bairro = "?"
        endereco_tag = card.find('span', class_='card-text')
        if endereco_tag:
             bairro = endereco_tag.get_text(strip=True)

        area, quartos, vagas, banheiros = self._extrair_icones(card)

        return Imovel(
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

    def _extrair_icones(self, card: Tag):
        area = quartos = vagas = banheiros = "?"
        icones = card.find_all('div', class_='container-icon')
        
        for div in icones:
            texto = div.get_text(strip=True).lower()
            if 'm²' in texto: 
                area = texto
            elif 'quarto' in texto: 
                quartos = texto.replace('quartos', '').replace('quarto', '').strip()
            elif 'vaga' in texto: 
                vagas = texto.replace('vagas', '').replace('vaga', '').strip()
            elif 'banheiro' in texto: 
                banheiros = texto.replace('banheiros', '').replace('banheiro', '').strip()
        
        return area, quartos, vagas, banheiros