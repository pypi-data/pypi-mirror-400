"""
Job de Sincronização de Comissões com OKING Hub
==================================================

Autor: Sistema OKING Hub
Data: 2025
Versão: 2.0.0 (Padrão OKING Hub com utils.final_query)

Descrição:
    Sincroniza comissões do ERP com o OKING Hub, processando em lotes
    configuráveis. Segue o padrão job_send_clients com query vindo da API.

Features:
    - Processamento em lotes (tamanho_pacote configurável)
    - Query vem da API via utils.final_query (não há SQL fixo)
    - Thread-safe com Lock
    - Semaphore check antes de executar
    - Validação de operação (okvendas/okinghub)
    - Logging completo de progresso
    - Tratamento robusto de erros

Dependências:
    - src.api.entities.comissao (Comissao)
    - src.api.okinghub (post_comissoes)
    - src.database.queries (IntegrationType, get_semaphore_command_data_sincronizacao)
    - src.database.connection (Connection)
    - src.jobs.utils (get_database_config, final_query, executa_comando_sql)

Exemplo de Uso:
    config = {
        'send_logs': True,
        'tamanho_pacote': 500,
        'executar_query_semaforo': 'S',
        'sql': 'SELECT ... FROM ... LEFT JOIN semaforo ...'  # Query da API
    }
    job_sincroniza_comissao(config)
"""

import logging
from typing import List, Optional
from datetime import datetime
from threading import Lock

# Importações internas
from src.api.entities.comissao import Comissao
from src.api import okinghub
from src.database import queries
import src.database.connection as database
import src.database.utils as utils
from src.log_types import LogType
from src.jobs.system_jobs import OnlineLogger
from src.jobs.utils import executa_comando_sql
import src

# Logger
logger = logging.getLogger(__name__)
send_log = OnlineLogger.send_log

# Lock para sincronização
lock = Lock()

# Constantes
BATCH_SIZE = 1000  # Tamanho do lote (configurável)
JOB_NAME = 'SINCRONIZA_COMISSAO'


def job_sincroniza_comissao(job_config: dict) -> None:
    """
    Job principal de sincronização de comissões (padrão OKING Hub - similar a job_send_clients)
    """
    with lock:
        send_logs = job_config.get('send_logs', True)
        db_config = utils.get_database_config(job_config)
        
        logger.info(f'[{JOB_NAME}] ==== THREAD INICIADA - job: {job_config.get("job_name")}')
        
        # LOG de Inicialização
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            'COMISSAO - Iniciado',
            LogType.EXEC,
            'COMISSAO')
        
        # Executar query semáforo se configurado
        if job_config.get('executar_query_semaforo') == 'S':
            executa_comando_sql(db_config, job_config)
        
        try:
            # Verificar operação (okvendas ou okinghub)
            operacao = src.client_data.get('operacao', '').lower()
            logger.info(f"[{JOB_NAME}] Operacao detectada: '{operacao}'")
            
            if 'okvendas' in operacao or 'okinghub' in operacao:
                logger.info(f"[{JOB_NAME}] Usando get_comissoes (banco semáforo)")
                comissoes_list = get_comissoes(job_config, db_config)
                
                logger.info(f'[{JOB_NAME}] Consultou as comissões')
                if len(comissoes_list) <= 0:
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        'Nenhuma comissão retornada para integração no momento',
                        LogType.WARNING,
                        'COMISSAO')
                    return
                
                logger.info(f'[{JOB_NAME}] Total de comissões: {len(comissoes_list)}')
                
                # Processar em lotes
                stats = {
                    'total_registros': len(comissoes_list),
                    'total_lotes': 0,
                    'total_sucesso': 0,
                    'total_erro': 0,
                    'inicio': datetime.now()
                }
                
                for i in range(0, len(comissoes_list), BATCH_SIZE):
                    batch_number = (i // BATCH_SIZE) + 1
                    batch_rows = comissoes_list[i:i + BATCH_SIZE]
                    
                    logger.info(f'[{JOB_NAME}] Processando lote {batch_number}/{(len(comissoes_list) + BATCH_SIZE - 1) // BATCH_SIZE}')
                    
                    try:
                        result = process_batch(batch_rows, batch_number, job_config, db_config)
                        
                        stats['total_lotes'] += 1
                        stats['total_sucesso'] += result.get('total_sucesso', 0)
                        stats['total_erro'] += result.get('total_erro', 0)
                        
                        if result['sucesso']:
                            logger.info(f'[{JOB_NAME}] Lote {batch_number} enviado com sucesso')
                        else:
                            logger.error(f'[{JOB_NAME}] Lote {batch_number} falhou: {result.get("mensagem")}')
                    
                    except Exception as e:
                        logger.error(f'[{JOB_NAME}] Erro ao processar lote {batch_number}: {str(e)}')
                        stats['total_erro'] += len(batch_rows)
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Erro no lote {batch_number}: {str(e)}',
                            LogType.ERROR,
                            'COMISSAO')
                
                # Estatísticas finais
                stats['fim'] = datetime.now()
                stats['duracao'] = (stats['fim'] - stats['inicio']).total_seconds()
                log_final_statistics(stats, job_config)
            
            else:
                logger.warning(f"[{JOB_NAME}] Operação '{operacao}' não suportada para sincronização de comissões")
        
        except Exception as e:
            logger.error(f'[{JOB_NAME}] Erro crítico: {str(e)}')
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Erro crítico na sincronização: {str(e)}',
                LogType.ERROR,
                'COMISSAO')


def get_comissoes(job_config: dict, db_config: utils.DatabaseConfig) -> List[dict]:
    """
    Busca comissões do banco (padrão OKING Hub - similar a get_clients)
    Query vem da API via db_config.sql
    """
    conn = database.Connection(db_config).get_conect()
    cursor = conn.cursor()
    try:
        # Usar utils.final_query para montar SQL com semáforo
        newsql = utils.final_query(db_config)
        
        if src.print_payloads:
            print(newsql)
        
        cursor.execute(newsql)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        cursor.close()
        conn.close()
        
        # Mapear rows para dicionários
        comissoes_list = []
        for row in results:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col.lower()] = row[i]
            comissoes_list.append(row_dict)
        
        logger.info(f"[{JOB_NAME}] get_comissoes | Total de comissões recuperadas: {len(comissoes_list)}")
        return comissoes_list
    
    except Exception as ex:
        logger.error(f"[{JOB_NAME}] get_comissoes | Erro: {str(ex)}")
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao consultar comissões: {str(ex)}',
            LogType.ERROR,
            'COMISSAO')
        return []


def process_batch(rows: List[dict], batch_number: int, job_config: dict, db_config) -> dict:
    """
    Processa um lote de comissões
    """
    send_logs = job_config.get('send_logs', True)
    
    try:
        # Converter rows para objetos Comissao
        comissoes = []
        
        for idx, row in enumerate(rows):
            try:
                # Passar todos os campos do row como kwargs
                # Campos extras (não definidos) serão capturados por **kwargs
                comissao = Comissao(**row)
                comissoes.append(comissao)
            except Exception as e:
                logger.error(f'[{JOB_NAME}] Erro ao converter row: {str(e)}')
                continue
        
        if not comissoes:
            logger.warning(f'[{JOB_NAME}] Lote {batch_number} sem comissões válidas')
            return {
                'sucesso': False,
                'mensagem': 'Nenhuma comissão válida no lote',
                'total_sucesso': 0,
                'total_erro': len(rows)
            }
        
        # Enviar via API
        logger.info(f'[{JOB_NAME}] Enviando {len(comissoes)} comissões (lote {batch_number})')
        result = okinghub.post_comissoes(send_logs, comissoes)
        
        # Atualizar semáforo individual
        if result.get('response'):
            validate_response_comissao(result.get('response'), rows, db_config, job_config)
        
        return result
        
    except Exception as e:
        logger.error(f'[{JOB_NAME}] Erro ao processar lote {batch_number}: {str(e)}')
        return {
            'sucesso': False,
            'mensagem': str(e),
            'total_sucesso': 0,
            'total_erro': len(rows)
        }


def validate_response_comissao(response, rows: List[dict], db_config, job_config: dict) -> None:
    """
    Valida resposta da API e atualiza semáforo para cada comissão
    """
    send_logs = job_config.get('send_logs', True)
    
    if not response:
        logger.warning(f"[{JOB_NAME}] validate_response_comissao | Resposta vazia")
        return
    
    if isinstance(response, str):
        logger.error(f"[{JOB_NAME}] validate_response_comissao | API retornou erro (string): {response}")
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'API retornou erro: {response[:200]}',
            LogType.ERROR,
            'COMISSAO')
        return
    
    if not isinstance(response, list):
        logger.error(f"[{JOB_NAME}] validate_response_comissao | Resposta não é lista: {type(response)}")
        return
    
    try:
        conexao = database.Connection(db_config)
        conn = conexao.get_conect()
        cursor = conn.cursor()

        for item in response:
            try:
                if not isinstance(item, dict):
                    logger.warning(f"[{JOB_NAME}] validate_response_comissao | Item não é dict: {type(item)}")
                    continue
                
                if 'identificador' not in item:
                    logger.warning(f"[{JOB_NAME}] validate_response_comissao | Item sem 'identificador': {item}")
                    continue
                
                identificador = str(item.get('identificador'))  # CODORDTRANS
                identificador2 = str(item.get('identificador2', ''))  # CODTRANSACAO
                
                sucesso_val = item.get('sucesso')
                if sucesso_val in (True, 1, '1', 'true', 'True', 'SUCESSO'):
                    msgret = item.get('mensagem', 'SUCESSO')[:150]
                else:
                    msgret = str(item.get('mensagem', item.get('Message', 'Erro desconhecido')))[:150]
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Erro ao enviar Comissão {identificador}/{identificador2}: {msgret}',
                        LogType.WARNING,
                        f'{identificador}-{identificador2}')
                
                cursor.execute(
                    queries.get_insert_update_semaphore_command(db_config.db_type),
                    queries.get_command_parameter(db_config.db_type, [
                        identificador,
                        identificador2,
                        queries.IntegrationType.COMISSAO.value,
                        msgret
                    ])
                )
                
            except Exception as e:
                logger.error(f"[{JOB_NAME}] validate_response_comissao | Erro ao processar item: {str(e)}")
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Erro ao processar item da resposta: {str(e)}',
                    LogType.ERROR,
                    'COMISSAO')
        
        cursor.close()
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.exception(f"[{JOB_NAME}] validate_response_comissao | Erro geral: {str(e)}")
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao validar resposta da API: {str(e)}',
            LogType.ERROR,
            'COMISSAO')


def log_final_statistics(stats: dict, job_config: dict) -> None:
    """
    Loga estatísticas finais da sincronização
    """
    logger.info(f'[{JOB_NAME}] ===== ESTATÍSTICAS FINAIS =====')
    logger.info(f'[{JOB_NAME}] Total de registros: {stats["total_registros"]}')
    logger.info(f'[{JOB_NAME}] Total de lotes: {stats["total_lotes"]}')
    logger.info(f'[{JOB_NAME}] Sucesso: {stats["total_sucesso"]}')
    logger.info(f'[{JOB_NAME}] Erro: {stats["total_erro"]}')
    logger.info(f'[{JOB_NAME}] Duração: {stats.get("duracao", 0):.2f}s')
    
    if stats['total_registros'] > 0:
        taxa_sucesso = (stats['total_sucesso'] / stats['total_registros']) * 100
        logger.info(f'[{JOB_NAME}] Taxa de sucesso: {taxa_sucesso:.2f}%')
    
    send_log(
        job_config.get('job_name'),
        job_config.get('enviar_logs'),
        job_config.get('enviar_logs_debug'),
        f'Sincronização concluída: {stats["total_registros"]} registros, '
        f'{stats["total_lotes"]} lotes, {stats["total_sucesso"]} sucesso, '
        f'{stats["total_erro"]} erro, {stats.get("duracao", 0):.2f}s',
        LogType.INFO,
        'COMISSAO')
