"""
Job de Sincronização de Contas a Receber com OKING Hub
========================================================

Autor: Sistema OKING Hub
Data: 2025-10-31
Versão: 1.0.0

Descrição:
    Sincroniza contas a receber (duplicatas/títulos) do ERP com o OKING Hub,
    processando em lotes configuráveis via tamanho_pacote (default: 1000).
    Segue o padrão OKING Hub (similar a job_send_clients e comission_jobs).

Features:
    - Processamento em lotes (batch size dinâmico via tamanho_pacote)
    - Query vem da API (campo comando_sql)
    - Utiliza utils.final_query para semáforo
    - Lock thread-safe
    - Identificadores: codcabrecpag + cgccpf
    - Suporte a Oracle, Firebird, SQL Server, MySQL

Dependências:
    - src.api.entities.contas_a_receber (ContasAReceber)
    - src.api.okinghub (post_contas_a_receber)
    - src.database.queries (IntegrationType)
    - src.database.connection (Connection)
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from threading import Lock

# Importações internas
from src.api.entities.contas_a_receber import ContasAReceber
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
DEFAULT_BATCH_SIZE = 1000  # Tamanho padrão do lote
JOB_NAME = 'SINCRONIZA_CONTAS_RECEBER'


def job_sincroniza_contas_receber(job_config: dict) -> None:
    """
    Job principal de sincronização de contas a receber (padrão OKING Hub - similar a job_send_clients)
    """
    with lock:
        # Obter tamanho_pacote dinâmico (com fallback para 1000)
        tamanho_pacote = job_config.get('tamanho_pacote')
        if tamanho_pacote is None or tamanho_pacote == 0 or not isinstance(tamanho_pacote, int):
            tamanho_pacote = DEFAULT_BATCH_SIZE
            logger.info(f'[{JOB_NAME}] tamanho_pacote não configurado, usando default: {DEFAULT_BATCH_SIZE}')
        else:
            logger.info(f'[{JOB_NAME}] tamanho_pacote configurado: {tamanho_pacote}')
        
        db_config = utils.get_database_config(job_config)
        
        logger.info(f'[{JOB_NAME}] ==== THREAD INICIADA - job: {job_config.get("job_name")}')
        
        # LOG de Inicialização
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            'CONTAS_A_RECEBER - Iniciado',
            LogType.EXEC,
            'CONTAS_A_RECEBER')
        
        # Executar query semáforo se configurado
        if job_config.get('executar_query_semaforo') == 'S':
            executa_comando_sql(db_config, job_config)
        
        try:
            # Verificar operação (okvendas ou okinghub)
            operacao = src.client_data.get('operacao', '').lower()
            logger.info(f"[{JOB_NAME}] Operacao detectada: '{operacao}'")
            
            if 'okvendas' in operacao or 'okinghub' in operacao:
                logger.info(f"[{JOB_NAME}] Usando get_contas_receber (banco semáforo)")
                contas_list = get_contas_receber(job_config, db_config)
                
                logger.info(f'[{JOB_NAME}] Consultou as contas a receber')
                if len(contas_list) <= 0:
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        'Nenhuma conta a receber retornada para integração no momento',
                        LogType.WARNING,
                        'CONTAS_A_RECEBER')
                    return
                
                logger.info(f'[{JOB_NAME}] Total de contas a receber: {len(contas_list)}')
                
                # Processar em lotes
                stats = {
                    'total_registros': len(contas_list),
                    'total_lotes': 0,
                    'total_sucesso': 0,
                    'total_erro': 0,
                    'inicio': datetime.now()
                }
                
                for i in range(0, len(contas_list), tamanho_pacote):
                    batch_number = (i // tamanho_pacote) + 1
                    batch_rows = contas_list[i:i + tamanho_pacote]
                    
                    logger.info(f'[{JOB_NAME}] Processando lote {batch_number}/{(len(contas_list) + tamanho_pacote - 1) // tamanho_pacote}')
                    
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
                            'CONTAS_A_RECEBER')
                
                # Estatísticas finais
                stats['fim'] = datetime.now()
                stats['duracao'] = (stats['fim'] - stats['inicio']).total_seconds()
                log_final_statistics(stats, job_config)
            
            else:
                logger.warning(f"[{JOB_NAME}] Operação '{operacao}' não suportada para sincronização de contas a receber")
        
        except Exception as e:
            logger.error(f'[{JOB_NAME}] Erro crítico: {str(e)}')
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Erro crítico na sincronização: {str(e)}',
                LogType.ERROR,
                'CONTAS_A_RECEBER')


def get_contas_receber(job_config: dict, db_config: utils.DatabaseConfig) -> List[dict]:
    """
    Busca contas a receber do banco (padrão OKING Hub - similar a get_clients)
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
        contas_list = []
        for row in results:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col.lower()] = row[i]
            contas_list.append(row_dict)
        
        logger.info(f"[{JOB_NAME}] get_contas_receber | Total de contas a receber recuperadas: {len(contas_list)}")
        return contas_list
    
    except Exception as ex:
        logger.error(f"[{JOB_NAME}] get_contas_receber | Erro: {str(ex)}")
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao consultar contas a receber: {str(ex)}',
            LogType.ERROR,
            'CONTAS_A_RECEBER')
        return []


def process_batch(batch: List[Dict[str, Any]], batch_number: int, job_config: dict, db_config) -> Dict[str, Any]:
    """
    Processa um lote de contas a receber (padrão OKING Hub)
    
    Args:
        batch: Lista de dicionários com dados das contas
        batch_number: Número do lote atual
        job_config: Configuração do job
        db_config: Configuração do banco de dados
    
    Returns:
        Dict com sucesso (bool), mensagem, total_sucesso, total_erro
    """
    send_logs = job_config.get('send_logs', True)
    
    result = {
        'sucesso': True,
        'mensagem': '',
        'total_sucesso': 0,
        'total_erro': 0
    }
    
    try:
        # Converter batch para objetos ContasAReceber
        contas = []
        for row in batch:
            try:
                # Passar todos os campos do row como kwargs
                # Campos extras (não definidos) serão capturados por **kwargs
                conta = ContasAReceber(**row)
                contas.append(conta)
            except Exception as e:
                logger.error(f'[{JOB_NAME}] Erro ao criar objeto ContasAReceber: {str(e)}')
                result['total_erro'] += 1
                continue
        
        if not contas:
            logger.warning(f'[{JOB_NAME}] Lote {batch_number}: Nenhuma conta válida')
            result['sucesso'] = False
            result['mensagem'] = 'Nenhuma conta válida no lote'
            return result
        
        logger.info(f'[{JOB_NAME}] Lote {batch_number}: Enviando {len(contas)} contas para API...')
        
        # Enviar para API
        api_response = okinghub.post_contas_a_receber(send_logs, contas)
        
        # Validar resposta
        validation_result = validate_response_contas_receber(
            api_response=api_response,
            batch=batch,
            job_config=job_config,
            db_config=db_config
        )
        
        result['total_sucesso'] = validation_result['sucesso']
        result['total_erro'] = validation_result['erro']
        result['sucesso'] = validation_result['sucesso'] > 0
        result['mensagem'] = f'{validation_result["sucesso"]} sucesso, {validation_result["erro"]} erro'
    
    except Exception as e:
        logger.error(f'[{JOB_NAME}] Lote {batch_number}: Erro ao processar: {str(e)}', exc_info=True)
        result['sucesso'] = False
        result['total_erro'] = len(batch)
        result['mensagem'] = str(e)
    
    return result


def validate_response_contas_receber(
    api_response: dict,
    batch: List[Dict[str, Any]],
    job_config: dict,
    db_config
) -> Dict[str, int]:
    """
    Valida resposta da API e atualiza semáforo (padrão OKING Hub)
    
    Args:
        api_response: Resposta da API post_contas_a_receber
        batch: Lista de dicionários com dados originais
        job_config: Configuração do job
        db_config: Configuração do banco de dados
    
    Returns:
        Dict com contadores de sucesso e erro
    """
    send_logs = job_config.get('send_logs', True)
    
    result = {'sucesso': 0, 'erro': 0}
    
    try:
        # Verificar se API retornou sucesso
        if not api_response.get('sucesso'):
            logger.error(f'[{JOB_NAME}] API retornou erro: {api_response.get("mensagem")}')
            result['erro'] = len(batch)
            return result
        
        # Obter lista de respostas individuais
        response_list = api_response.get('response', [])
        
        if not isinstance(response_list, list):
            logger.warning(f'[{JOB_NAME}] API não retornou lista de respostas, usando totais agregados')
            result['sucesso'] = api_response.get('total_sucesso', 0)
            result['erro'] = api_response.get('total_erro', 0)
            
            # Atualizar semáforo para todos (assumindo sucesso)
            if result['sucesso'] > 0:
                insert_update_semaphore_receivables(
                    batch=batch,
                    job_config=job_config,
                    db_config=db_config,
                    status='SUCESSO'
                )
            
            return result
        
        # Validar respostas individuais
        logger.info(f'[{JOB_NAME}] Validando {len(response_list)} respostas individuais...')
        
        successful_items = []
        
        for idx, response_item in enumerate(response_list):
            if idx >= len(batch):
                break
            
            original_item = batch[idx]
            
            try:
                # Verificar sucesso do item
                sucesso_val = response_item.get('sucesso') if isinstance(response_item, dict) else False
                
                # Aceitar múltiplos formatos de sucesso
                if sucesso_val in (True, 1, '1', 'true', 'True', 'SUCESSO'):
                    result['sucesso'] += 1
                    successful_items.append(original_item)
                else:
                    result['erro'] += 1
                    mensagem_erro = response_item.get('mensagem', 'Erro desconhecido') if isinstance(response_item, dict) else 'Erro desconhecido'
                    logger.warning(f'[{JOB_NAME}] Conta {original_item.get("codcabrecpag")} com erro: {mensagem_erro}')
            
            except Exception as e:
                logger.error(f'[{JOB_NAME}] Erro ao validar resposta do item {idx}: {str(e)}')
                result['erro'] += 1
        
        # Atualizar semáforo apenas para itens com sucesso
        if successful_items:
            logger.info(f'[{JOB_NAME}] Atualizando semáforo para {len(successful_items)} itens bem-sucedidos...')
            insert_update_semaphore_receivables(
                batch=successful_items,
                job_config=job_config,
                db_config=db_config,
                status='SUCESSO'
            )
        
        logger.info(f'[{JOB_NAME}] Validação concluída: {result["sucesso"]} sucesso, {result["erro"]} erro')
        
    except Exception as e:
        logger.error(f'[{JOB_NAME}] Erro ao validar resposta: {str(e)}', exc_info=True)
        result['erro'] = len(batch)
    
    return result


def insert_update_semaphore_receivables(
    batch: List[Dict[str, Any]],
    job_config: dict,
    db_config,
    status: str
) -> None:
    """
    Atualiza semáforo para contas a receber processadas (padrão OKING Hub)
    
    Identificadores:
        - identificador: codcabrecpag (VARCHAR 100)
        - identificador2: cgccpf (VARCHAR 100)
        - tipo_id: 28 (IntegrationType.CONTAS_A_RECEBER)
    
    Args:
        batch: Lista de dicionários com dados das contas
        job_config: Configuração do job
        db_config: Configuração do banco de dados
        status: Status a ser registrado ('SUCESSO' ou 'ERRO')
    """
    try:
        conn = database.Connection(db_config).get_conect()
        cursor = conn.cursor()
        
        # Obter comando MERGE/UPSERT apropriado
        merge_command = queries.get_semaphore_command_data_sincronizacao(db_config.db_type)
        
        # Preparar parâmetros
        params = []
        for item in batch:
            codcabrecpag = str(item.get('codcabrecpag', ''))
            cgccpf = str(item.get('cgccpf', ''))
            
            if not codcabrecpag:
                logger.warning(f'[{JOB_NAME}] Item sem codcabrecpag, pulando semáforo')
                continue
            
            # (identificador, identificador2, tipo_id, mensagem)
            params.append((
                codcabrecpag,
                cgccpf,
                queries.IntegrationType.CONTAS_A_RECEBER.value,
                status
            ))
        
        if not params:
            logger.warning(f'[{JOB_NAME}] Nenhum parâmetro válido para semáforo')
            return
        
        # Executar em lote
        logger.info(f'[{JOB_NAME}] Atualizando semáforo para {len(params)} registros...')
        
        if db_config.db_type.lower() == 'mysql':
            cursor.executemany(merge_command, params)
        else:
            for param in params:
                cursor.execute(merge_command, param)
        
        conn.commit()
        logger.info(f'[{JOB_NAME}] Semáforo atualizado com sucesso')
        
    except Exception as e:
        logger.error(f'[{JOB_NAME}] Erro ao atualizar semáforo: {str(e)}', exc_info=True)
        conn.rollback()
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao atualizar semáforo: {str(e)}',
            LogType.ERROR,
            'CONTAS_A_RECEBER')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def log_final_statistics(stats: dict, job_config: dict) -> None:
    """
    Registra estatísticas finais da sincronização (padrão OKING Hub)
    
    Args:
        stats: Dicionário com estatísticas (total_registros, total_lotes, total_sucesso, total_erro, duracao)
        job_config: Configuração do job
    """
    logger.info(f'[{JOB_NAME}] ========================================')
    logger.info(f'[{JOB_NAME}] RESUMO DA SINCRONIZAÇÃO')
    logger.info(f'[{JOB_NAME}] ========================================')
    logger.info(f'[{JOB_NAME}] Total de registros: {stats["total_registros"]}')
    logger.info(f'[{JOB_NAME}] Total de lotes: {stats["total_lotes"]}')
    logger.info(f'[{JOB_NAME}] Total sucesso: {stats["total_sucesso"]}')
    logger.info(f'[{JOB_NAME}] Total erro: {stats["total_erro"]}')
    logger.info(f'[{JOB_NAME}] Duração: {stats["duracao"]:.2f} segundos')
    logger.info(f'[{JOB_NAME}] ========================================')
    
    # Log online
    send_log(
        job_config.get('job_name'),
        job_config.get('enviar_logs'),
        job_config.get('enviar_logs_debug'),
        f'Sincronização concluída: {stats["total_sucesso"]} sucesso, {stats["total_erro"]} erro em {stats["duracao"]:.2f}s',
        LogType.INFO,
        'CONTAS_A_RECEBER'
    )
