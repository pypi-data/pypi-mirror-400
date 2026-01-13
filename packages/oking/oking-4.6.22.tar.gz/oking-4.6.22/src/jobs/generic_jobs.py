"""
Módulo responsável pela execução de JOBS GENÉRICOS

Este módulo permite criar novos jobs sem necessidade de código específico.
Jobs genéricos são configurados no painel OKING Web e executados dinamicamente.

Fluxo:
1. Consultar ERP com SQL configurado no painel
2. Verificar duplicatas no semáforo
3. Converter resultados para dicionários (nomes reais das colunas)
4. Enviar para API genérica
5. Gravar no semáforo após sucesso

Autor: OKING HUB Team
Data: 29/10/2025
"""

import logging
from typing import List, Dict, Any, Optional
from threading import Lock

import src
import src.database.connection as database
from src.database import utils
from src.database import queries
from src.database.utils import DatabaseConfig
from src.jobs.system_jobs import OnlineLogger
from src.log_types import LogType

logger = logging.getLogger()
send_log = OnlineLogger.send_log
lock = Lock()


def get_or_create_generic_type_id(job_name: str, db_config: DatabaseConfig) -> Optional[int]:
    """
    Obtém ou cria o tipo_id para um job genérico na tabela openk_semaforo.tipo
    
    Nomenclatura: Remove sufixo '_job' e adiciona '_GEN'
    Exemplo: 'envia_comissao_job' → 'ENVIA_COMISSAO_GEN'
    
    Args:
        job_name: Nome do job (ex: 'envia_comissao_job')
        db_config: Configuração do banco semáforo
        
    Returns:
        ID do tipo ou None se erro
    """
    try:
        # 1. Gerar nome do tipo
        # Remove sufixo '_job' e converte para maiúsculas
        tipo_nome = job_name.replace('_job', '').upper() + '_GEN'
        
        logger.info(f'[GENERIC] Verificando tipo: {tipo_nome}')
        
        # 2. Conectar ao banco semáforo
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()
        
        # 3. Verificar se tipo já existe
        # CORREÇÃO (04/11/2025): db_config é objeto, não dict
        select_query = queries.get_select_tipo_by_name_command(db_config.db_type)
        cursor.execute(select_query, [tipo_nome])
        result = cursor.fetchone()
        
        if result:
            tipo_id = result[0]
            logger.info(f'[GENERIC] Tipo já existe: {tipo_nome} (ID: {tipo_id})')
            cursor.close()
            conn.close()
            return tipo_id
        
        # 4. Tipo não existe, criar novo
        logger.info(f'[GENERIC] Criando novo tipo: {tipo_nome}')
        
        # CORREÇÃO (04/11/2025): db_config é objeto, não dict
        insert_query = queries.get_insert_tipo_command(db_config.db_type)
        cursor.execute(insert_query, [tipo_nome])
        conn.commit()
        
        # 5. Obter ID recém criado
        # CORREÇÃO (04/11/2025): db_config é objeto, não dict
        if db_config.db_type.lower() == 'oracle':
            cursor.execute(queries.get_last_inserted_tipo_id_command(db_config.db_type))
            tipo_id = cursor.fetchone()[0]
        elif db_config.db_type.lower() == 'firebird':
            # Firebird: buscar por nome após insert
            cursor.execute(queries.get_select_tipo_by_name_after_insert_command(db_config.db_type), [tipo_nome])
            tipo_id = cursor.fetchone()[0]
        else:  # SQL Server
            cursor.execute(queries.get_last_inserted_tipo_id_command(db_config.db_type))
            tipo_id = cursor.fetchone()[0]
        
        logger.info(f'[GENERIC] Tipo criado: {tipo_nome} (ID: {tipo_id})')
        
        cursor.close()
        conn.close()
        
        return tipo_id
        
    except Exception as e:
        logger.error(f'[GENERIC] Erro ao obter/criar tipo: {str(e)}')
        return None


def check_semaphore_exists(
    identificador: str,
    identificador2: str,
    tipo_id: int,
    db_config: DatabaseConfig
) -> bool:
    """
    Verifica se registro já existe no semáforo
    
    Args:
        identificador: Valor da primeira coluna do SELECT
        identificador2: Valor da segunda coluna do SELECT
        tipo_id: ID do tipo na tabela tipo
        db_config: Configuração do banco
        
    Returns:
        True se já existe, False caso contrário
    """
    try:
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()
        
        # CORREÇÃO (04/11/2025): db_config é objeto, não dict
        query = queries.get_check_semaphore_exists_command(db_config.db_type)
        cursor.execute(query, [str(identificador), str(identificador2), tipo_id])
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return count > 0
        
    except Exception as e:
        logger.error(f'[GENERIC] Erro ao verificar semáforo: {str(e)}')
        return False


def check_semaphore_batch(
    records: List[tuple],
    tipo_id: int,
    db_config: DatabaseConfig
) -> set:
    """
    Verifica quais registros já existem no semáforo EM LOTE (otimizado)
    
    Args:
        records: Lista de tuplas (identificador, identificador2)
        tipo_id: ID do tipo na tabela tipo
        db_config: Configuração do banco
        
    Returns:
        Set com tuplas (identificador, identificador2) que JÁ EXISTEM
    """
    if not records:
        return set()
    
    try:
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()
        
        # Montar query IN com placeholders
        placeholders = ','.join(['(?, ?, ?)'] * len(records))
        query = f"""
            SELECT identificador, identificador2 
            FROM openk_semaforo.semaforo 
            WHERE (identificador, identificador2, tipo_id) IN ({placeholders})
        """
        
        # Preparar parâmetros: lista achatada de [id1, id2, tipo, id1, id2, tipo, ...]
        params = []
        for identificador, identificador2 in records:
            params.extend([str(identificador), str(identificador2), tipo_id])
        
        cursor.execute(query, params)
        existing = set((row[0], row[1]) for row in cursor.fetchall())
        
        cursor.close()
        conn.close()
        
        logger.info(f'[GENERIC] Verificação em lote: {len(existing)}/{len(records)} já existem')
        return existing
        
    except Exception as e:
        logger.error(f'[GENERIC] Erro ao verificar semáforo em lote: {str(e)}')
        # Em caso de erro, retorna vazio (assume que nada existe)
        return set()


def insert_semaphore(
    identificador: str,
    identificador2: str,
    tipo_id: int,
    db_config: DatabaseConfig,
    mensagem: str = 'Enviado com sucesso'
) -> bool:
    """
    Insere registro no semáforo
    
    Args:
        identificador: Valor da primeira coluna
        identificador2: Valor da segunda coluna
        tipo_id: ID do tipo
        db_config: Configuração do banco
        mensagem: Mensagem opcional
        
    Returns:
        True se sucesso, False se erro
    """
    try:
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()
        
        # CORREÇÃO (04/11/2025): db_config é objeto, não dict
        query = queries.get_insert_semaphore_generic_command(db_config.db_type)
        cursor.execute(query, [str(identificador), str(identificador2), tipo_id, mensagem])
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f'[GENERIC] Erro ao inserir semáforo: {str(e)}')
        return False


def execute_generic_query(sql: str, db_config: DatabaseConfig) -> List[tuple]:
    """
    Executa query SQL genérica no banco ERP
    
    Args:
        sql: Query SQL configurada no painel
        db_config: Configuração do banco ERP
        
    Returns:
        Lista de tuplas com resultados
    """
    try:
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()
        
        if src.print_payloads:
            print(sql)
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        logger.info(f'[GENERIC] Query retornou {len(rows)} registros')
        
        cursor.close()
        conn.close()
        
        return rows
        
    except Exception as e:
        logger.error(f'[GENERIC] Erro ao executar query: {str(e)}')
        raise


def get_column_names_from_query(sql: str, db_config: DatabaseConfig) -> List[str]:
    """
    Obtém nomes das colunas da query SQL
    
    Args:
        sql: Query SQL
        db_config: Configuração do banco
        
    Returns:
        Lista com nomes das colunas
    """
    try:
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()
        
        # Para queries com CTE (WITH), não podemos colocar em subconsulta
        # Vamos usar uma abordagem diferente: adicionar TOP 0 / WHERE ROWNUM=0 / FIRST 0
        sql_trimmed = sql.strip()
        sql_lower = sql_trimmed.lower()
        
        # Remover ponto-e-vírgula final se existir
        if sql_trimmed.endswith(';'):
            sql_trimmed = sql_trimmed[:-1].strip()
        
        # Detectar se é CTE (começa com WITH)
        is_cte = sql_lower.startswith('with')
        
        if db_config.db_type.lower() == 'oracle':
            if is_cte:
                # CTE: adicionar WHERE ROWNUM = 0 no final
                query_metadata = f"{sql_trimmed} AND ROWNUM = 0" if 'where' in sql_lower else f"{sql_trimmed} WHERE ROWNUM = 0"
            else:
                query_metadata = f"SELECT * FROM ({sql_trimmed}) WHERE ROWNUM = 0"
                
        elif db_config.db_type.lower() == 'firebird':
            if is_cte:
                # Firebird: adicionar FIRST 0 após SELECT
                query_metadata = sql_trimmed.replace('SELECT ', 'SELECT FIRST 0 ', 1)
            else:
                query_metadata = f"SELECT FIRST 0 * FROM ({sql_trimmed})"
                
        else:  # SQL Server
            if is_cte:
                # CTE: adicionar TOP 0 após o último SELECT (SELECT principal após as CTEs)
                # Estratégia: encontrar o último SELECT que não está dentro de subquery
                
                # Remover ponto e vírgula final se existir
                sql_clean = sql_trimmed.rstrip(';').strip()
                
                # Tentar encontrar o SELECT principal (após todas as CTEs)
                # Procurar por padrão: ) SELECT ou , SELECT (indicando fim de CTE)
                import re
                
                # Padrão para encontrar o SELECT principal após CTEs
                # Busca por ) seguido de SELECT ou , seguido de SELECT (fim das CTEs)
                cte_end_pattern = r'\)\s*,\s*tmp_\w+\s+AS\s*\('  # Próxima CTE
                main_select_pattern = r'\)\s+(SELECT)'  # SELECT principal após última CTE
                
                # Encontrar a última ocorrência do SELECT principal
                matches = list(re.finditer(main_select_pattern, sql_clean, re.IGNORECASE))
                
                if matches:
                    # Pegar a última ocorrência (SELECT principal)
                    last_match = matches[-1]
                    # Inserir TOP 0 após o SELECT
                    pos = last_match.start(1) + 6  # Após "SELECT"
                    query_metadata = sql_clean[:pos] + ' TOP 0' + sql_clean[pos:]
                else:
                    # Fallback: método alternativo - inserir TOP 0 no último SELECT
                    # Dividir por SELECT e pegar o último
                    parts = re.split(r'\bSELECT\b', sql_clean, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        # Reconstruir com TOP 0 no último SELECT
                        query_metadata = 'SELECT'.join(parts[:-1]) + 'SELECT TOP 0' + parts[-1]
                    else:
                        query_metadata = sql_clean.replace('SELECT ', 'SELECT TOP 0 ', 1)
            else:
                query_metadata = f"SELECT TOP 0 * FROM ({sql_trimmed}) AS subquery"
        
        cursor.execute(query_metadata)
        
        # Obter nomes das colunas
        column_names = [desc[0].lower() for desc in cursor.description]
        
        cursor.close()
        conn.close()
        
        logger.info(f'[GENERIC] Colunas detectadas: {column_names}')
        
        return column_names
        
    except Exception as e:
        logger.error(f'[GENERIC] Erro ao obter nomes das colunas: {str(e)}')
        raise


def convert_rows_to_dicts(rows: List[tuple], column_names: List[str]) -> List[Dict[str, Any]]:
    """
    Converte tuplas em dicionários com nomes reais das colunas
    
    Args:
        rows: Lista de tuplas do banco
        column_names: Lista com nomes das colunas
        
    Returns:
        Lista de dicionários
    """
    result = []
    
    for row in rows:
        row_dict = {}
        for i, col_name in enumerate(column_names):
            # Converter valores para tipos JSON-safe
            value = row[i]
            
            # Tratar tipos especiais
            if value is None:
                row_dict[col_name] = None
            elif isinstance(value, (int, float, str, bool)):
                row_dict[col_name] = value
            else:
                # Converter outros tipos para string
                row_dict[col_name] = str(value)
        
        result.append(row_dict)
    
    return result


def job_generic(job_config: dict):
    """
    Job genérico para processar qualquer tipo de integração configurada no painel
    
    FLUXO:
    1. Obter/criar tipo_id no semáforo
    2. Obter nomes das colunas da query
    3. Executar query no ERP
    4. Para cada registro:
       a. Verificar se já existe no semáforo (duplicata)
       b. Se não existir, converter para dict e enviar para API
       c. Se sucesso, gravar no semáforo
    5. Logs detalhados de cada etapa
    
    Args:
        job_config: Configuração do job vinda da API
            - job_name: Nome do job (ex: 'envia_comissao_job')
            - comando_sql: Query SQL a executar
            - enviar_logs: Flag de logs
            - enviar_logs_debug: Flag de logs debug
            - db_host, db_port, etc: Configuração banco ERP
    """
    with lock:
        try:
            # ===== ETAPA 1: INICIALIZAÇÃO =====
            logger.info(f'==== [GENERIC] JOB INICIADO: {job_config.get("job_name")}')
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                'Job Genérico - Iniciado',
                LogType.EXEC,
                f'{job_config.get("job_name")}')
            
            # ===== ETAPA 2: VALIDAR SQL =====
            # CORREÇÃO (04/11/2025): get_config() salva comando_sql como 'sql'
            sql = job_config.get('sql') or job_config.get('comando_sql')
            if not sql:
                logger.error('[GENERIC] SQL não configurado no job')
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    'Erro: SQL não configurado',
                    LogType.ERROR,
                    f'{job_config.get("job_name")}_EP_2')
                return
            
            # ===== ETAPA 3: CONFIGURAÇÕES DO BANCO =====
            db_config_erp = utils.get_database_config(job_config)
            
            # ===== ETAPA 4: OBTER/CRIAR TIPO NO SEMÁFORO =====
            tipo_id = get_or_create_generic_type_id(job_config.get('job_name'), db_config_erp)
            if not tipo_id:
                logger.error('[GENERIC] Não foi possível obter/criar tipo no semáforo')
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    'Erro ao obter/criar tipo no semáforo',
                    LogType.ERROR,
                    f'{job_config.get("job_name")}_EP_4')
                return
            
            # ===== ETAPA 5: OBTER NOMES DAS COLUNAS =====
            try:
                column_names = get_column_names_from_query(sql, db_config_erp)
            except Exception as e:
                logger.error(f'[GENERIC] Erro ao obter colunas: {str(e)}')
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Erro ao obter colunas da query: {str(e)}',
                    LogType.ERROR,
                    f'{job_config.get("job_name")}_EP_5')
                return
            
            # Validar que tem pelo menos 2 colunas (identificador + identificador2)
            if len(column_names) < 2:
                logger.error(f'[GENERIC] Query deve ter pelo menos 2 colunas, encontrado: {len(column_names)}')
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Query deve ter pelo menos 2 colunas (identificador + identificador2)',
                    LogType.ERROR,
                    f'{job_config.get("job_name")}_EP_6')
                return
            
            # ===== ETAPA 6: EXECUTAR QUERY NO ERP =====
            try:
                rows = execute_generic_query(sql, db_config_erp)
            except Exception as e:
                logger.error(f'[GENERIC] Erro ao executar query no ERP: {str(e)}')
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Erro ao executar query no ERP: {str(e)}',
                    LogType.ERROR,
                    f'{job_config.get("job_name")}_EP_7')
                return
            
            # ===== ETAPA 7: VALIDAR SE HÁ DADOS =====
            if len(rows) == 0:
                logger.info('[GENERIC] Nenhum registro retornado da query')
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    'Nenhum registro retornado do ERP',
                    LogType.WARNING,
                    f'{job_config.get("job_name")}')
                return
            
            # ===== ETAPA 8: CONVERTER PARA DICIONÁRIOS =====
            all_data = convert_rows_to_dicts(rows, column_names)
            
            logger.info(f'[GENERIC] Total de registros: {len(all_data)}')
            
            # ===== ETAPA 9: FILTRAR DUPLICATAS E PREPARAR DADOS (OTIMIZADO EM LOTE) =====
            # CORREÇÃO (13/11/2025): Verificação em lote ao invés de 1 por 1
            # Antes: 56.457 queries SELECT individuais -> deadlock
            # Depois: 1 query com IN para todos os registros
            
            logger.info(f'[GENERIC] Verificando duplicatas em lote...')
            
            # Preparar lista de identificadores para verificar em lote
            identifiers_to_check = [
                (str(record[column_names[0]]), str(record[column_names[1]]) if len(column_names) > 1 else '')
                for record in all_data
            ]
            
            # Verificar todos de uma vez (1 query SQL com IN)
            existing_set = check_semaphore_batch(identifiers_to_check, tipo_id, db_config_erp)
            
            # Filtrar registros novos
            data_to_send = []
            skipped_count = 0
            
            for record in all_data:
                identificador = str(record[column_names[0]])
                identificador2 = str(record[column_names[1]]) if len(column_names) > 1 else ''
                
                if (identificador, identificador2) in existing_set:
                    skipped_count += 1
                    if job_config.get('enviar_logs_debug'):
                        logger.debug(f'[GENERIC] Registro já existe: {identificador}/{identificador2}')
                else:
                    data_to_send.append(record)
            
            logger.info(f'[GENERIC] Registros novos: {len(data_to_send)}, Já existentes: {skipped_count}')
            
            if len(data_to_send) == 0:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Todos os {len(all_data)} registros já foram enviados anteriormente',
                    LogType.INFO,
                    f'{job_config.get("job_name")}')
                return
            
            # ===== ETAPA 10: ENVIAR PARA API (EM LOTE) =====
            # CORREÇÃO (05/11/2025): Implementado envio em lotes para melhor performance
            # Antes: ~1000 chamadas API para 1000 registros
            # Depois: ~20 chamadas API para 1000 registros (batches de 50)
            import src.api.okinghub as api_okinghub
            
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Iniciando envio de {len(data_to_send)} registros para API',
                LogType.INFO,
                f'{job_config.get("job_name")}')
            
            # Obter tamanho do pacote (padrão: 50)
            batch_size = job_config.get('tamanho_pacote') or 50
            if not isinstance(batch_size, int) or batch_size <= 0:
                batch_size = 50
            
            total_records = len(data_to_send)
            total_batches = (total_records + batch_size - 1) // batch_size
            
            logger.info(f'[GENERIC] Processando {total_records} registros em {total_batches} lotes de até {batch_size}')
            
            success_count = 0
            error_count = 0
            batch_num = 0
            
            # ✅ PROCESSAR EM LOTES
            for i in range(0, total_records, batch_size):
                batch_num += 1
                batch = data_to_send[i:i + batch_size]
                batch_actual_size = len(batch)
                
                logger.info(f'[GENERIC] Lote {batch_num}/{total_batches} ({batch_actual_size} registros)')
                
                try:
                    # Enviar lote completo para API
                    result = api_okinghub.post_generic_data_batch(
                        job_config.get('enviar_logs'),
                        job_config.get('job_name'),
                        batch
                    )
                    
                    if not result['sucesso']:
                        logger.error(f'[GENERIC] Erro no lote {batch_num}: {result["mensagem"]}')
                        error_count += batch_actual_size
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Erro no lote {batch_num}: {result["mensagem"]}',
                            LogType.ERROR,
                            f'{job_config.get("job_name")}_EP_8')
                        continue
                    
                    # Processar resultados individuais do lote
                    resultados = result.get('resultados', [])
                    
                    if len(resultados) != batch_actual_size:
                        logger.warning(f'[GENERIC] Lote {batch_num}: esperado {batch_actual_size} resultados, recebido {len(resultados)}')
                    
                    # Processar cada resultado
                    for idx, response in enumerate(resultados):
                        try:
                            # Obter dados originais do registro
                            original_record = batch[idx] if idx < len(batch) else {}
                            
                            # Obter identificadores
                            identificador = str(original_record[column_names[0]])
                            identificador2 = str(original_record[column_names[1]]) if len(column_names) > 1 else ''
                            
                            # Processar resultado
                            if response.sucesso:
                                success_count += 1
                                
                                # Gravar no semáforo
                                inserted = insert_semaphore(
                                    identificador,
                                    identificador2,
                                    tipo_id,
                                    db_config_erp,
                                    'Enviado com sucesso'
                                )
                                
                                if not inserted:
                                    logger.warning(f'[GENERIC] Enviado mas não gravou no semáforo: {identificador}/{identificador2}')
                                
                                if job_config.get('enviar_logs_debug'):
                                    logger.info(f'[GENERIC] Sucesso: {identificador}/{identificador2}')
                            
                            else:
                                error_count += 1
                                erro_msg = response.mensagem[:2000] if response.mensagem else 'Erro desconhecido'
                                logger.error(f'[GENERIC] API rejeitou: {identificador}/{identificador2} - {erro_msg}')
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Erro ao enviar [{identificador}/{identificador2}]: {erro_msg}',
                                    LogType.ERROR,
                                    f'{job_config.get("job_name")}_EP_9')
                        
                        except Exception as e:
                            error_count += 1
                            identificador = str(original_record.get(column_names[0], 'UNKNOWN'))
                            identificador2 = str(original_record.get(column_names[1], ''))
                            logger.error(f'[GENERIC] Exceção ao processar resultado: {identificador}/{identificador2} - {str(e)}')
                    
                    # Log do progresso do lote
                    logger.info(f'[GENERIC] Lote {batch_num}/{total_batches} concluído - Sucesso: {result["total_sucesso"]}, Erro: {result["total_erro"]}')
                
                except Exception as e:
                    # Erro ao processar lote completo
                    error_count += batch_actual_size
                    logger.error(f'[GENERIC] Erro crítico no lote {batch_num}: {str(e)}')
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Erro crítico no lote {batch_num}: {str(e)}',
                        LogType.ERROR,
                        f'{job_config.get("job_name")}_EP_10')
            
            # ===== ETAPA 11: LOG FINAL =====
            logger.info(f'[GENERIC] Job finalizado: {success_count} sucesso, {error_count} erro(s)')
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Finalizado: {success_count} sucesso, {error_count} erro(s), {skipped_count} já existentes',
                LogType.EXEC,
                f'{job_config.get("job_name")}')
        
        except Exception as e:
            logger.critical(f'[GENERIC] Erro crítico: {str(e)}', exc_info=True)
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'ERRO CRÍTICO: {str(e)}',
                LogType.ERROR,
                f'{job_config.get("job_name")}_EP_20')
            raise
