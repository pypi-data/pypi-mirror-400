"""
Entity: Contas a Receber (Receivables)
========================================

Representa uma conta a receber do ERP para sincronização com OKING Hub.

Autor: Sistema OKING Hub
Data: 2025-10-31
Versão: 1.0.0

Estrutura:
    - 71 campos da tabela MySQL contas_a_receber
    - Serialização JSON com tratamento de datetime
    - Validação de tipos
    - Compatível com API OKING Hub

Uso:
    conta = ContasAReceber(
        codcabrecpag=123456,
        referencia='REF-001',
        documento='NFE-12345',
        valor=1500.00,
        ...
    )
    payload = conta.toJSON()
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional


class ContasAReceber:
    """
    Representa uma conta a receber (duplicata/título) do sistema ERP
    
    Attributes:
        codcabrecpag: Código único da conta a receber (PK no ERP)
        referencia: Referência/identificador adicional
        documento: Número do documento (nota fiscal, boleto, etc)
        valor: Valor principal do título
        valorpg: Valor pago
        datavcto: Data de vencimento
        emissao: Data de emissão
        cgccpf: CPF/CNPJ do cliente
        codclifor: Código do cliente/fornecedor
        ... (71 campos no total)
    """
    
    def __init__(
        self,
        # Campos principais
        codcabrecpag: int,
        referencia: Optional[str] = None,
        codfilial: Optional[int] = None,
        datalimi: Optional[datetime] = None,
        datavcto: Optional[datetime] = None,
        emissao: Optional[datetime] = None,
        documento: Optional[str] = None,
        valor: Optional[float] = None,
        valorpg: Optional[float] = None,
        valorjurosdesc: Optional[float] = None,
        valordev: Optional[float] = None,
        valordcom: Optional[float] = None,
        cotacao: Optional[float] = None,
        cotacaobaixa: Optional[float] = None,
        juros: Optional[float] = None,
        juroslimi: Optional[float] = None,
        multa: Optional[float] = None,
        antecipacao: Optional[float] = None,
        pontualidade: Optional[float] = None,
        tipojuro: Optional[str] = None,
        tipojurovcto: Optional[str] = None,
        obs: Optional[str] = None,
        fdatabase: Optional[float] = None,
        fdatavcto: Optional[float] = None,
        fiof: Optional[float] = None,
        fiofembutido: Optional[float] = None,
        tipoantec: Optional[str] = None,
        codfilial_empresa: Optional[int] = None,
        tipodoc: Optional[str] = None,
        vlradicional: Optional[float] = None,
        efeito2: Optional[str] = None,
        nrobloqueto: Optional[str] = None,
        nossonumero: Optional[str] = None,
        d_dtassinat: Optional[datetime] = None,
        desc_const: Optional[float] = None,
        vlrjurosdiario: Optional[float] = None,
        naoconciliado: Optional[int] = None,
        codfatura: Optional[int] = None,
        vlrantecipacaodiario: Optional[float] = None,
        datadesconto: Optional[datetime] = None,
        codcrsituacao: Optional[str] = None,
        codclifor: Optional[int] = None,
        classifica: Optional[str] = None,
        codunidclifor: Optional[int] = None,
        cgccpf: Optional[str] = None,
        datalimcredito: Optional[datetime] = None,
        limcredito: Optional[float] = None,
        codmoedalim: Optional[str] = None,
        efeito: Optional[str] = None,
        codgrupoclifor: Optional[str] = None,
        codgrupoclifor2: Optional[str] = None,
        ecliente: Optional[bool] = None,
        eforneced: Optional[bool] = None,
        etransportador: Optional[bool] = None,
        clienteavista: Optional[str] = None,
        respcobranca: Optional[int] = None,
        respcobranca_nome: Optional[str] = None,
        nomeprodutor: Optional[str] = None,
        vctolimcredito: Optional[datetime] = None,
        categoria: Optional[str] = None,
        descsetor: Optional[str] = None,
        codimovelrural: Optional[int] = None,
        codformapgto: Optional[int] = None,
        codbandeira: Optional[int] = None,
        codbanco: Optional[int] = None,
        codbancodia: Optional[int] = None,
        cobranca: Optional[str] = None,
        codmoeda: Optional[str] = None,
        codperfilfin: Optional[int] = None,
        ultbaixa: Optional[datetime] = None,
        codcobrador: Optional[int] = None,
        codtipotr: Optional[str] = None,
        desctipotr: Optional[str] = None,
        descsitduplicata: Optional[str] = None,
        **kwargs
    ):
        """
        Inicializa uma conta a receber com todos os campos da tabela MySQL
        
        Args:
            codcabrecpag: Código único da conta (obrigatório)
            referencia: Referência adicional
            documento: Número do documento
            valor: Valor principal
            ... (demais campos opcionais)
            **kwargs: Campos extras dinâmicos
        """
        # Campo obrigatório
        self.codcabrecpag = codcabrecpag
        
        # Campos de identificação
        self.referencia = referencia
        self.documento = documento
        self.codfilial = codfilial
        self.codfilial_empresa = codfilial_empresa
        
        # Datas
        self.datalimi = datalimi
        self.datavcto = datavcto
        self.emissao = emissao
        self.d_dtassinat = d_dtassinat
        self.datadesconto = datadesconto
        self.datalimcredito = datalimcredito
        self.vctolimcredito = vctolimcredito
        self.ultbaixa = ultbaixa
        
        # Valores monetários principais
        self.valor = valor
        self.valorpg = valorpg
        self.valorjurosdesc = valorjurosdesc
        self.valordev = valordev
        self.valordcom = valordcom
        
        # Valores de câmbio e taxas
        self.cotacao = cotacao
        self.cotacaobaixa = cotacaobaixa
        
        # Valores de encargos
        self.juros = juros
        self.juroslimi = juroslimi
        self.multa = multa
        self.antecipacao = antecipacao
        self.pontualidade = pontualidade
        self.vlrjurosdiario = vlrjurosdiario
        self.vlrantecipacaodiario = vlrantecipacaodiario
        self.desc_const = desc_const
        self.vlradicional = vlradicional
        
        # Tipos e configurações
        self.tipojuro = tipojuro
        self.tipojurovcto = tipojurovcto
        self.tipoantec = tipoantec
        self.tipodoc = tipodoc
        self.codtipotr = codtipotr
        self.desctipotr = desctipotr
        
        # Campos financeiros
        self.fdatabase = fdatabase
        self.fdatavcto = fdatavcto
        self.fiof = fiof
        self.fiofembutido = fiofembutido
        
        # Dados bancários e cobrança
        self.nrobloqueto = nrobloqueto
        self.nossonumero = nossonumero
        self.codformapgto = codformapgto
        self.codbandeira = codbandeira
        self.codbanco = codbanco
        self.codbancodia = codbancodia
        self.cobranca = cobranca
        self.codmoeda = codmoeda
        self.codmoedalim = codmoedalim
        self.codperfilfin = codperfilfin
        self.codcobrador = codcobrador
        
        # Situação e controle
        self.codcrsituacao = codcrsituacao
        self.descsitduplicata = descsitduplicata
        self.naoconciliado = naoconciliado
        self.codfatura = codfatura
        self.efeito = efeito
        self.efeito2 = efeito2
        
        # Dados do cliente
        self.codclifor = codclifor
        self.codunidclifor = codunidclifor
        self.cgccpf = cgccpf
        self.classifica = classifica
        self.limcredito = limcredito
        self.codgrupoclifor = codgrupoclifor
        self.codgrupoclifor2 = codgrupoclifor2
        self.ecliente = ecliente
        self.eforneced = eforneced
        self.etransportador = etransportador
        self.clienteavista = clienteavista
        self.respcobranca = respcobranca
        self.respcobranca_nome = respcobranca_nome
        self.nomeprodutor = nomeprodutor
        self.categoria = categoria
        self.descsetor = descsetor
        self.codimovelrural = codimovelrural
        
        # Observações
        self.obs = obs
        
        # Campos extras dinâmicos
        self.__dict__.update(kwargs)
    
    def toJSON(self) -> dict:
        """
        Serializa o objeto para JSON compatível com a API OKING Hub
        
        Trata especialmente:
            - datetime → string no formato ISO (YYYY-MM-DD HH:MM:SS)
            - Decimal → float
            - None → mantém como null
            - bool → 0 ou 1
            - **kwargs dinâmicos são incluídos automaticamente
        
        Returns:
            dict: Dicionário JSON-serializável
        
        Example:
            >>> conta = ContasAReceber(codcabrecpag=123, emissao=datetime.now(), campo_extra='valor')
            >>> json_data = conta.toJSON()
            >>> print(json_data['emissao'])
            '2025-10-31 14:30:00'
            >>> print(json_data['campo_extra'])
            'valor'
        """
        result = {
            # Campo obrigatório
            "codcabrecpag": self.codcabrecpag,
            
            # Identificação
            "referencia": self.referencia,
            "documento": self.documento,
            "codfilial": self.codfilial,
            "codfilial_empresa": self.codfilial_empresa,
            
            # Datas (serialização para string)
            "datalimi": self.datalimi.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.datalimi, datetime) else str(self.datalimi) if self.datalimi else None,
            "datavcto": self.datavcto.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.datavcto, datetime) else str(self.datavcto) if self.datavcto else None,
            "emissao": self.emissao.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.emissao, datetime) else str(self.emissao) if self.emissao else None,
            "d_dtassinat": self.d_dtassinat.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.d_dtassinat, datetime) else str(self.d_dtassinat) if self.d_dtassinat else None,
            "datadesconto": self.datadesconto.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.datadesconto, datetime) else str(self.datadesconto) if self.datadesconto else None,
            "datalimcredito": self.datalimcredito.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.datalimcredito, datetime) else str(self.datalimcredito) if self.datalimcredito else None,
            "vctolimcredito": self.vctolimcredito.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.vctolimcredito, datetime) else str(self.vctolimcredito) if self.vctolimcredito else None,
            "ultbaixa": self.ultbaixa.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.ultbaixa, datetime) else str(self.ultbaixa) if self.ultbaixa else None,
            
            # Valores monetários
            "valor": float(self.valor) if self.valor is not None else None,
            "valorpg": float(self.valorpg) if self.valorpg is not None else None,
            "valorjurosdesc": float(self.valorjurosdesc) if self.valorjurosdesc is not None else None,
            "valordev": float(self.valordev) if self.valordev is not None else None,
            "valordcom": float(self.valordcom) if self.valordcom is not None else None,
            "cotacao": float(self.cotacao) if self.cotacao is not None else None,
            "cotacaobaixa": float(self.cotacaobaixa) if self.cotacaobaixa is not None else None,
            "juros": float(self.juros) if self.juros is not None else None,
            "juroslimi": float(self.juroslimi) if self.juroslimi is not None else None,
            "multa": float(self.multa) if self.multa is not None else None,
            "antecipacao": float(self.antecipacao) if self.antecipacao is not None else None,
            "pontualidade": float(self.pontualidade) if self.pontualidade is not None else None,
            "vlrjurosdiario": float(self.vlrjurosdiario) if self.vlrjurosdiario is not None else None,
            "vlrantecipacaodiario": float(self.vlrantecipacaodiario) if self.vlrantecipacaodiario is not None else None,
            "desc_const": float(self.desc_const) if self.desc_const is not None else None,
            "vlradicional": float(self.vlradicional) if self.vlradicional is not None else None,
            "fdatabase": float(self.fdatabase) if self.fdatabase is not None else None,
            "fdatavcto": float(self.fdatavcto) if self.fdatavcto is not None else None,
            "fiof": float(self.fiof) if self.fiof is not None else None,
            "fiofembutido": float(self.fiofembutido) if self.fiofembutido is not None else None,
            "limcredito": float(self.limcredito) if self.limcredito is not None else None,
            
            # Tipos e configurações
            "tipojuro": self.tipojuro,
            "tipojurovcto": self.tipojurovcto,
            "tipoantec": self.tipoantec,
            "tipodoc": self.tipodoc,
            "codtipotr": self.codtipotr,
            "desctipotr": self.desctipotr,
            
            # Dados bancários
            "nrobloqueto": self.nrobloqueto,
            "nossonumero": self.nossonumero,
            "codformapgto": self.codformapgto,
            "codbandeira": self.codbandeira,
            "codbanco": self.codbanco,
            "codbancodia": self.codbancodia,
            "cobranca": self.cobranca,
            "codmoeda": self.codmoeda,
            "codmoedalim": self.codmoedalim,
            "codperfilfin": self.codperfilfin,
            "codcobrador": self.codcobrador,
            
            # Situação
            "codcrsituacao": self.codcrsituacao,
            "descsitduplicata": self.descsitduplicata,
            "naoconciliado": self.naoconciliado,
            "codfatura": self.codfatura,
            "efeito": self.efeito,
            "efeito2": self.efeito2,
            
            # Dados do cliente
            "codclifor": self.codclifor,
            "codunidclifor": self.codunidclifor,
            "cgccpf": self.cgccpf,
            "classifica": self.classifica,
            "codgrupoclifor": self.codgrupoclifor,
            "codgrupoclifor2": self.codgrupoclifor2,
            "ecliente": 1 if self.ecliente else 0 if self.ecliente is not None else None,
            "eforneced": 1 if self.eforneced else 0 if self.eforneced is not None else None,
            "etransportador": 1 if self.etransportador else 0 if self.etransportador is not None else None,
            "clienteavista": self.clienteavista,
            "respcobranca": self.respcobranca,
            "respcobranca_nome": self.respcobranca_nome,
            "nomeprodutor": self.nomeprodutor,
            "categoria": self.categoria,
            "descsetor": self.descsetor,
            "codimovelrural": self.codimovelrural,
            
            # Observações
            "obs": self.obs
        }
        
        # Adicionar campos extras dinâmicos (kwargs) automaticamente
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
        """Representação string do objeto para debug"""
        return (f"ContasAReceber(codcabrecpag={self.codcabrecpag}, "
                f"documento='{self.documento}', "
                f"valor={self.valor}, "
                f"datavcto={self.datavcto})")
    
    def __str__(self) -> str:
        """String legível do objeto"""
        return f"Conta a Receber #{self.codcabrecpag} - Doc: {self.documento} - R$ {self.valor:.2f if self.valor else 0}"
