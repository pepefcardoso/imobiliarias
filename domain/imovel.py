from dataclasses import dataclass
from typing import Optional

@dataclass
class Imovel:
    titulo: str
    preco: str
    link: str
    imobiliaria_origem: str
    codigo: Optional[str] = None
    bairro: Optional[str] = None
    area: Optional[str] = None
    quartos: Optional[str] = None
    banheiros: Optional[str] = None
    vagas: Optional[str] = None

    def to_dict(self):
        return {
            "Imobiliaria": self.imobiliaria_origem,
            "Codigo": self.codigo,
            "Bairro": self.bairro,
            "Titulo": self.titulo,
            "Area": self.area,
            "Quartos": self.quartos,
            "Banheiros": self.banheiros,
            "Vagas": self.vagas,
            "Preco": self.preco,
            "Link": self.link
        }