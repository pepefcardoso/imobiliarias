import json
from typing import Dict, Any
from bs4 import BeautifulSoup
from interfaces.i_parser import IParser
from domain.imovel import Imovel
from domain.scraper_result import ScraperResult

class QualAlugarParser(IParser):
    def parse(self, html_content: str) -> ScraperResult:
        resultado = ScraperResult()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        script_data = soup.find('script', id='__NEXT_DATA__')
        
        if not script_data:
            resultado.erros.append("Não encontrei os dados estruturados (__NEXT_DATA__).")
            return resultado

        try:
            json_content = json.loads(script_data.string)
            lista_imoveis_raw = json_content.get('props', {}).get('pageProps', {}).get('imoveis', [])
        except Exception as e:
            resultado.erros.append(f"Erro ao ler JSON interno: {str(e)}")
            return resultado

        if not lista_imoveis_raw:
            resultado.erros.append("Lista de imóveis vazia no JSON.")
            return resultado

        for item in lista_imoveis_raw:
            try:
                imovel = self._processar_item(item)
                if imovel:
                    resultado.imoveis.append(imovel)
            except Exception as e:
                resultado.erros.append(f"Erro no item {item.get('imv_codigo', '?')}: {str(e)}")
                
        return resultado

    def _processar_item(self, item: Dict[str, Any]) -> Imovel:
        titulo = item.get('imv_titulo')
        if not titulo:
            return None 
        
        codigo = str(item.get('imv_cod_gaia', '?'))
        bairro = item.get('imv_bairro', '?')
        link_relativo = item.get('url_amiga', '#')
        link = f"https://www.qualalugar.net{link_relativo}" if link_relativo.startswith('/') else link_relativo
        
        valor_num = item.get('imv_preco_locacao')
        preco = f"R$ {valor_num}" if valor_num else "Consultar"
        
        area_num = item.get('imv_area_util')
        area = f"{area_num} m²" if area_num else "?"
        
        quartos = str(item.get('imv_qtd_dorm', '?'))
        banheiros = str(item.get('imv_qtd_banheiros', '?'))
        vagas = str(item.get('imv_qtd_vagas', '?'))

        return Imovel(
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