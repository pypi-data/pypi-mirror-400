from datetime import datetime

import requests as req
import jsonpickle
import logging

logger = logging.getLogger()


class Module:
    def __init__(self, executar_query_semaforo: str, job: str, comando_sql: str, unidade_tempo: str,
                 tempo_execucao: int, old_version='N', ultima_execucao: datetime = '', ativo: str = 'N',
                 query_final: str = 'S', semaforo_sql: str = 'N', enviar_logs_slack: bool = False,
                 enviar_logs_debug: bool = False, **kwargs):
        self.job_name = job
        self.ativo = ativo
        self.executar_query_semaforo = executar_query_semaforo
        self.sql = comando_sql
        self.time_unit = unidade_tempo
        self.time = tempo_execucao
        self.query_final = query_final
        self.exists_sql = semaforo_sql
        self.send_logs = enviar_logs_slack
        self.enviar_logs_debug = enviar_logs_debug
        self.ultima_execucao = ultima_execucao
        self.old_version = old_version
        self.__dict__.update(kwargs)


def get(url: str, params: dict = None):
    response = req.get(url, params)
    if str(response.status_code).startswith('2'):
        return jsonpickle.decode(response.content)
    else:
        logger.error(f'Erro ao executar GET: {url} | Code: {response.status_code} | {response.content}')

    return None


class Response:
    """Classe para retorno padronizado de API"""
    def __init__(self, data=None, status_code=200):
        self.data = data
        self.status_code = status_code


def get_filtros(shortname: str, token: str):
    """
    Busca configurações/filtros da API do OKING Hub
    
    Args:
        shortname: Identificador da empresa (não utilizado, mantido por compatibilidade)
        token: Token de autenticação
        
    Returns:
        Response object com os dados
    """
    try:
        # Usa base_url do token_manager para suportar URLs customizadas
        token_manager = TokenManager()
        base_url = token_manager.get_base_url()
        url = f'https://{base_url}/api/consulta/oking_hub/filtros?token={token}'
        response = req.get(url)
        
        if response.status_code == 200:
            return Response(data=response.json(), status_code=200)
        else:
            logger.error(f'Erro ao buscar filtros: {response.status_code} | {response.text}')
            return None
            
    except Exception as e:
        logger.error(f'Erro ao buscar filtros: {e}')
        return None
