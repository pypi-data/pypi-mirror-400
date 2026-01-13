"""
Entity para Comissão

Representa os dados de comissão enviados para API OKING Hub.
Endpoint: POST /api/hub_comissao

Autor: OKING HUB Team
Data: 29/10/2025
"""

from typing import Optional
from datetime import datetime


class Comissao:
    """
    Representa um registro de comissão
    """
    
    def __init__(
        self,
        numero_nota_fiscal: int,
        codigo_vendedor: int,
        data_emissao: str,
        codigo_da_filial: int,
        nome_da_filial: str,
        codordtrans: int,
        codtransacao: str,
        cfop_nota_fiscal: str,
        preco_unitario: float,
        data_vencimento: str,
        quantidade: float,
        serie: str,
        referencia: str,
        numero_cupom: int,
        total_nota_fiscal: float,
        codigo_produto: int,
        codigo_fornecedor: int,
        codigo_cliente: int,
        cgccpf: str,
        codunidclifor: int,
        quantidade_pontos: float,
        preco_manual: float,
        quantidade_original: float,
        codigo_multiplicador: str,
        descricao_multiplicador: str,
        pureza: float,
        total_convertido: float,
        **kwargs
    ):
        self.numero_nota_fiscal = numero_nota_fiscal
        self.codigo_vendedor = codigo_vendedor
        self.data_emissao = data_emissao
        self.codigo_da_filial = codigo_da_filial
        self.nome_da_filial = nome_da_filial
        self.codordtrans = codordtrans
        self.codtransacao = codtransacao
        self.cfop_nota_fiscal = cfop_nota_fiscal
        self.preco_unitario = preco_unitario
        self.data_vencimento = data_vencimento
        self.quantidade = quantidade
        self.serie = serie
        self.referencia = referencia
        self.numero_cupom = numero_cupom
        self.total_nota_fiscal = total_nota_fiscal
        self.codigo_produto = codigo_produto
        self.codigo_fornecedor = codigo_fornecedor
        self.codigo_cliente = codigo_cliente
        self.cgccpf = cgccpf
        self.codunidclifor = codunidclifor
        self.quantidade_pontos = quantidade_pontos
        self.preco_manual = preco_manual
        self.quantidade_original = quantidade_original
        self.codigo_multiplicador = codigo_multiplicador
        self.descricao_multiplicador = descricao_multiplicador
        self.pureza = pureza
        self.total_convertido = total_convertido
        
        # Campos extras dinâmicos
        self.__dict__.update(kwargs)

    def toJSON(self) -> dict:
        """
        Converte para dicionário (formato JSON)
        Inclui campos dinâmicos automaticamente via **kwargs
        """
        # Garantir que campos datetime sejam serializáveis para JSON
        def _fmt(dt):
            if dt is None:
                return None
            if isinstance(dt, datetime):
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return str(dt)

        result = {
            "numero_nota_fiscal": self.numero_nota_fiscal,
            "codigo_vendedor": self.codigo_vendedor,
            "data_emissao": _fmt(self.data_emissao),
            "codigo_da_filial": self.codigo_da_filial,
            "nome_da_filial": self.nome_da_filial,
            "codordtrans": self.codordtrans,
            "codtransacao": self.codtransacao,
            "cfop_nota_fiscal": self.cfop_nota_fiscal,
            "preco_unitario": self.preco_unitario,
            "data_vencimento": _fmt(self.data_vencimento),
            "quantidade": self.quantidade,
            "serie": self.serie,
            "referencia": self.referencia,
            "numero_cupom": self.numero_cupom,
            "total_nota_fiscal": self.total_nota_fiscal,
            "codigo_produto": self.codigo_produto,
            "codigo_fornecedor": self.codigo_fornecedor,
            "codigo_cliente": self.codigo_cliente,
            "cgccpf": self.cgccpf,
            "codunidclifor": self.codunidclifor,
            "quantidade_pontos": self.quantidade_pontos,
            "preco_manual": self.preco_manual,
            "quantidade_original": self.quantidade_original,
            "codigo_multiplicador": self.codigo_multiplicador,
            "descricao_multiplicador": self.descricao_multiplicador,
            "pureza": self.pureza,
            "total_convertido": self.total_convertido
        }
        
        # Adicionar campos extras dinâmicos (kwargs) automaticamente
        from decimal import Decimal
        for key, value in self.__dict__.items():
            if key not in result:
                # Tratar tipos especiais para campos dinâmicos
                if isinstance(value, datetime):
                    result[key] = value.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(value, Decimal):
                    result[key] = float(value)
                elif isinstance(value, bool):
                    result[key] = 1 if value else 0
                else:
                    result[key] = value
        
        return result

    def __repr__(self) -> str:
        return f"Comissao(nf={self.numero_nota_fiscal}, vendedor={self.codigo_vendedor}, valor={self.total_nota_fiscal})"


class ComissaoResponse:
    """
    Representa a resposta da API após envio de comissões
    """
    
    def __init__(
        self,
        sucesso: bool,
        mensagem: str,
        protocolo: Optional[str] = None,
        total_processado: Optional[int] = None
    ):
        self.sucesso = sucesso
        self.mensagem = mensagem
        self.protocolo = protocolo
        self.total_processado = total_processado

    def __repr__(self) -> str:
        return f"ComissaoResponse(sucesso={self.sucesso}, protocolo={self.protocolo})"
