import re
from typing import Optional
from bs4 import BeautifulSoup, Tag
from interfaces.i_parser import IParser
from domain.imovel import Imovel
from domain.scraper_result import ScraperResult

class BilcomParser(IParser):
    def parse(self, html_content: str) -> ScraperResult:
        soup = BeautifulSoup(html_content, 'html.parser')
        resultado = ScraperResult()
        
        cards = soup.find_all('a', href=re.compile(r'^/imovel/'))
        
        seen_links = set()
        unique_cards = []
        for card in cards:
            href = card['href']
            if href not in seen_links:
                seen_links.add(href)
                unique_cards.append(card)

        if not unique_cards:
            resultado.erros.append("Nenhum imóvel encontrado (verifique se os seletores mudaram).")

        for card_tag in unique_cards:
            try:
                imovel = self._processar_card(card_tag)
                if imovel:
                    resultado.imoveis.append(imovel)
            except Exception as e:
                resultado.erros.append(f"Erro ao processar card Bilcom: {str(e)}")

        return resultado

    def _processar_card(self, card_tag: Tag) -> Optional[Imovel]:
        link_relativo = card_tag.get('href')
        link = f"https://bilcomimoveis.com.br{link_relativo}"

        titulo = "?"
        strongs = card_tag.find_all('strong')
        for s in strongs:
            text = s.get_text(strip=True)
            if "R$" not in text and "Pronto" not in text and len(text) > 10:
                titulo = text
                break
        
        preco = "Consultar"
        preco_tag = card_tag.find(string=re.compile(r'R\$\s*[\d.,]+'))
        if preco_tag:
            preco = preco_tag.strip()

        bairro = "?"
        address_tag = card_tag.find('address')
        if address_tag:
            full_address = address_tag.get_text(strip=True)
            if '-' in full_address:
                bairro = full_address.split('-')[0].strip()
            else:
                bairro = full_address

        quartos = "?"
        vagas = "?"
        area = "?"
        banheiros = "?"

        dl = card_tag.find('dl')
        if dl:
            items = dl.find_all('div') 
            for item in items:
                dt = item.find('dt')
                dd = item.find('dd')
                if dt and dd:
                    label = dt.get_text(strip=True).lower()
                    value = dd.get_text(strip=True)
                    
                    if 'dorm' in label or 'quarto' in label:
                        quartos = value
                    elif 'garag' in label or 'vaga' in label:
                        vagas = value
                    elif 'área' in label or 'area' in label:
                        area = value
                    elif 'banho' in label:
                        banheiros = value

        codigo = "?"
        ref_span = card_tag.find(string=re.compile(r'Ref\.:'))
        if ref_span:
            codigo = ref_span.replace('Ref.:', '').strip()
        else:
            match = re.search(r'/(\d+)$', link_relativo)
            if match:
                codigo = match.group(1)

        return Imovel(
            imobiliaria_origem="Bilcom",
            titulo=titulo,
            preco=preco,
            link=link,
            codigo=codigo,
            bairro=bairro,
            area=area,
            quartos=quartos,
            banheiros=banheiros,
            vagas=vagas
        )