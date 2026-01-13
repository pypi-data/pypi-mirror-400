import logging
import jsonpickle
import src
import requests
import json
from src.token_manager import TokenManager

from src.api.entities.estoque import Estoque
from src.api.entities.pedido import Queue, Order
from src.api.entities.preco import Preco
from src.api.entities.produto import Produto
from src.api.entities.service_fee import ServiceFee
from src.entities.invoice import Invoice
from src.entities.log import Log
from src.entities.response import GenericResponse

# from src.entities.orderb2b import OrderB2B
# from src.entities.orderb2c import OrderB2C

from typing import List

logger = logging.getLogger()


def send_stocks_hub(body: List[Estoque]) -> List[GenericResponse]:
    try:

        url = f'{src.client_data.get("url_api_principal")}/api/estoque'
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "access-token": src.client_data.get("token_oking"),
        }
        json_body = jsonpickle.encode(body, unpicklable=False)
        json_body = '{"lista":' + json_body + "}"

        if src.print_payloads:
            print(json_body)
        response = requests.post(url, json=json.loads(json_body), headers=headers)
        result = [GenericResponse(**t) for t in response.json()]
        return result
    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API {str(ex)}")


###############################################################


def post_prices(body: List[Preco]) -> List[GenericResponse]:
    try:

        url = f'{src.client_data.get("url_api_principal")}/api/preco'
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            # 'access-token': src.client_data.get('token_api')
        }

        json_body = jsonpickle.encode(body, unpicklable=False)
        json_body = '{"lista":' + json_body + "}"

        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        result = [GenericResponse(**t) for t in response.json()]
        return result
    # json_response = response.json()

    # if len(json_response) > 0:
    #    array_response = [json_response]
    #    result_dict = response_dict(json_response)
    # return result_dict
    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API HUB/api/preco {str(ex)}")


def post_products(body: List[Produto]) -> List[GenericResponse]:
    try:
        url = f'{src.client_data.get("url_api_principal")}/api/produto'
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            # 'access-token': src.client_data.get('token_api')
        }

        json_body = jsonpickle.encode(body, unpicklable=False)
        json_body = '{"lista":' + json_body + "}"

        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        result = [GenericResponse(**t) for t in response.json()]
        return result
    # json_response = response.json()

    # if len(json_response) > 0:
    #    array_response = [json_response]
    #    result_dict = response_dict(json_response)
    # return result_dict
    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API HUB/api/produto {str(ex)}")


def post_clients(body: List):
    try:
        url = f'{src.client_data.get("url_api_principal")}/api/cliente'
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            # 'access-token': src.client_data.get('token_oking')
        }

        json_body = jsonpickle.encode(body, unpicklable=False)
        json_body = '{"token":"' + src.client_data.get('token_oking') + '","lista":' + json_body + "}"

        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        if response.ok:
            response_data = response.json()
            
            # Validação: verifica se response_data é lista e se cada item é dict
            if not isinstance(response_data, list):
                logger.warning(f'Resposta da API não é uma lista: {type(response_data)} - {response_data}')
                return {
                    "error": "invalid_response",
                    "message": f"Resposta inválida da API: {response_data}"
                }
            
            result = []
            for t in response_data:
                if isinstance(t, dict):
                    result.append(GenericResponse(**t))
                else:
                    logger.warning(f'Item da resposta não é um dicionário: {type(t)} - {t}')
                    # Cria resposta de erro genérica
                    result.append(GenericResponse('', '', 3, f'Resposta inválida: {t}'))
            
            return result
        else:
            logger.warning(f"Erro {response.status_code}, {response.json()['message']}")
            return {
                "error": response.status_code,
                "message": response.json()["message"],
            }
    # json_response = response.json()

    # if len(json_response) > 0:
    #    array_response = [json_response]
    #    result_dict = response_dict(json_response)
    # return result_dict
    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API HUB/api/cliente {str(ex)}")
        raise ex


def post_vendas(body: List):
    try:
        url = f'{src.client_data.get("url_api_principal")}/api/venda'
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            # 'access-token': src.client_data.get('token_oking')
        }

        json_body = jsonpickle.encode(body, unpicklable=False)
        json_body = '{"lista":' + json_body + "}"

        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        if response.ok:
            result = [GenericResponse(**t) for t in response.json()]
            return result
        else:
            logger.warning(f"Erro {response.status_code}, {response.json()['message']}")
            return {
                "error": response.status_code,
                "message": response.json()["message"],
            }
    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API HUB/api/venda {str(ex)}")
        raise ex


def response_dict(resultado):
    lista = []
    for row in resultado:
        pdict = {
            "identificador": str(row["identificador"]),
            "sucesso": str(row["sucesso"]),
            "message": str(row["mensagem"]),
        }
        lista.append(pdict)

    return lista


###############################################################
def post_log(log: Log) -> bool:
    try:
        if not src.is_dev:
            # Usa base_url do token_manager para suportar URLs customizadas
            token_manager = TokenManager()
            base_url = token_manager.get_base_url()
            url = f"https://{base_url}/api/log_integracao"
            headers = {
                "Content-type": "application/json",
                "Accept": "application/json",
                "access-token": src.client_data.get("token_api"),
            }

            json_log = jsonpickle.encode(log, unpicklable=False)
            # if src.print_payloads:
            #    print(json_log)
            response = requests.post(url, json=json.loads(json_log), headers=headers)
            if response.ok:
                return True

            return False
        else:
            return True
    except Exception:
        return False


def check_update() -> dict:
    """
    Verifica se houve alteracoes nos modulos/jobs configurados na API.
    
    Endpoint otimizado que retorna apenas se ha atualizacoes pendentes,
    evitando buscar todos os modulos desnecessariamente.
    
    Returns:
        dict: {
            'isupdate': bool - True se ha atualizacoes pendentes,
            'data_alteracao': str - Data/hora da ultima alteracao (formato ISO),
            'qtd_jobs': int - Quantidade total de jobs configurados (opcional)
        }
        
    Exemplo de resposta da API:
        [{'isupdate': True, 'data_ultima_alteracao': '2025-11-11 10:26:18', 'ultimo_reload_client': None}]
    """
    try:
        if src.is_dev:
            # Em modo dev, sempre retorna sem atualizacao
            return {'isupdate': False, 'data_alteracao': None, 'qtd_jobs': 0}
        
        # Usa base_url do token_manager para suportar URLs customizadas
        token_manager = TokenManager()
        base_url = token_manager.get_base_url()
        url = f"https://{base_url}/api/checkupdate"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "access-token": src.client_data.get("token_oking")
        }
        
        # Token enviado no body tambem
        body = {
            'token': src.client_data.get('token_oking')
        }
        
        response = requests.post(url, json=body, headers=headers, timeout=10)
        
        if response.ok:
            data = response.json()
            # API retorna array com 1 objeto
            if isinstance(data, list) and len(data) > 0:
                result = data[0]
                return {
                    'isupdate': result.get('isupdate', False),
                    'data_alteracao': result.get('data_ultima_alteracao'),
                    'qtd_jobs': result.get('qtd_jobs', 0)
                }
            else:
                logger.warning(f"API checkupdate retornou formato inesperado: {data}")
                return {'isupdate': False, 'data_alteracao': None, 'qtd_jobs': 0}
        else:
            logger.warning(f"API checkupdate retornou status {response.status_code}")
            return {'isupdate': False, 'data_alteracao': None, 'qtd_jobs': 0}
            
    except requests.exceptions.Timeout:
        logger.error("Timeout ao verificar atualizacoes na API")
        return {'isupdate': False, 'data_alteracao': None, 'qtd_jobs': 0}
    except Exception as e:
        logger.error(f"Erro ao verificar atualizacoes: {str(e)}")
        return {'isupdate': False, 'data_alteracao': None, 'qtd_jobs': 0}


def confirm_reload() -> bool:
    """
    Confirma que o cliente recarregou os jobs com sucesso.
    
    Atualiza o campo ultimo_reload_client na API para que proximas
    verificacoes de checkupdate retornem isupdate=false ate haver nova alteracao.
    
    Returns:
        bool: True se confirmacao foi bem-sucedida, False caso contrario
    """
    try:
        if src.is_dev:
            return True
        
        # Usa base_url do token_manager para suportar URLs customizadas
        token_manager = TokenManager()
        base_url = token_manager.get_base_url()
        url = f"https://{base_url}/api/confirm_reload"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "access-token": src.client_data.get("token_oking")
        }
        
        body = {
            'token': src.client_data.get('token_oking')
        }
        
        response = requests.post(url, json=body, headers=headers, timeout=10)
        
        if response.ok:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                result = data[0]
                if result.get('sucesso'):
                    logger.info(f"Reload confirmado: {result.get('mensagem')}")
                    return True
            logger.warning(f"Confirmacao de reload retornou formato inesperado: {data}")
            return False
        else:
            logger.warning(f"API confirm_reload retornou status {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao confirmar reload: {str(e)}")
        return False


###############################################################
def get_order_queue(body: dict, stats) -> List[Queue]:
    retqueue = []
    try:
        url_api = body.get("url_api_secundaria") + "/api/consulta/pedido_fila/"
        token = body.get("token_oking")
        status = stats
        pagina = 0
        url = f"{url_api}filtros?token={token}&status={status}"
        response = requests.get(
            url,
            headers={"Accept": "application/json", "access-token": token},
            params={"pagina": pagina},
        )
        if response.text == "Retorno sem dados!":
            logger.warning(f"{response.text}")
        elif response.ok:
            retqueue = [Queue(**t) for t in response.json()]
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
    except Exception as ex:
        logger.error(
            f"Erro ao realizar GET na api oking hub {url}" + str(ex), exc_info=True
        )
        raise

    return retqueue


def get_order(body: dict, pedido_oking_id) -> Order:
    retorder = None
    try:
        url_api = body.get("url_api_secundaria") + "/api/consulta/pedido/filtros"
        response = requests.get(
            url_api,
            headers={
                "Accept": "application/json",
                "access-token": body.get("token_api"),
            },
            params={
                "token": body.get("token_oking"),
                "pedido_oking_id": pedido_oking_id,
            },
        )
        if response.ok:
            obj = jsonpickle.decode(response.content)
            retorder = Order(**obj)
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
    except Exception as ex:
        logger.error(f"Erro ao realizar GET na api oking hub {url_api} - {str(ex)}")
        raise

    return retorder


# def get_order_b2c(url: str, token: str, order_id: int) -> OrderB2C:
#     order = None
#     try:
#         response = requests.get(url.format(order_id), headers={'Accept': 'application/json', 'access-token': token})
#         if response.ok:
#             obj = jsonpickle.decode(response.content)
#             order = OrderB2C(**obj)
#         else:
#             logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
#     except Exception as ex:
#         logger.error(f'Erro ao realizar GET na api okvendas {url} - {str(ex)}')
#         raise
#
#     return order
# def get_order_b2b(url: str, token: str, order_id: int) -> OrderB2B:
#     order = None
#     try:
#         response = requests.get(url.format(order_id), headers={'Accept': 'application/json', 'access-token': token})
#         if response.ok:
#             obj = jsonpickle.decode(response.content)
#             order = OrderB2B(**obj)
#         else:
#             logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
#     except Exception as ex:
#         logger.error(f'Erro ao realizar GET na api okvendas {url} - {str(ex)}')
#         raise
#
#     return order


def post_order_erp_code(body) -> bool:
    url = src.client_data.get("url_api_principal") + "/api/pedido_integrado"
    token = src.client_data.get("token_api_integracao")
    try:
        if src.print_payloads:
            print(body)
        response = requests.post(
            url,
            json=body,
            headers={"Accept": "application/json", "access-token": token},
        )
        if response.ok:
            return True
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
            return False
    except Exception as ex:
        logger.error(
            f"Erro ao realizar GET na api okinghub {url}" + str(ex), exc_info=True
        )
        return False


def put_client_erp_code(body: dict) -> bool:
    url = src.client_data.get("url_api_principal") + "/cliente/codigo"
    token = (src.client_data.get("token_api_integracao"),)
    try:
        data = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(data)
        response = requests.put(
            url,
            data=json.loads(data),
            headers={"Accept": "application/json", "access-token": token},
        )
        if response.ok:
            return True
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
            return False
    except Exception as ex:
        logger.error(
            f"Erro ao realizar GET na api okinghub {url}" + str(ex), exc_info=True
        )
        return False


def put_protocol_orders(protocolos: List[str]) -> bool:
    url = src.client_data.get("url_api_secundaria") + f"/pedido/fila"
    try:
        json_protocolos = jsonpickle.encode(protocolos)
        if src.print_payloads:
            print(json_protocolos)
        response = requests.put(
            url,
            json=json.loads(json_protocolos),
            headers={
                "Accept": "application/json",
                "access-token": src.client_data.get("token_api"),
            },
        )
        if response.ok:
            return True
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
            return False
    except Exception as ex:
        logger.error(
            f"Erro ao protocolar pedidos na api oking hub {url}" + str(ex),
            exc_info=True,
        )
        return False


def post_faturar(invoice: Invoice) -> None | str | GenericResponse:
    """
    Enviar NF de um pedido para api okvendas
    Args:
        invoice: Objeto com os dados da NF

    Returns:
    None se o envio for sucesso. Caso falhe, um objeto contendo status e descrição do erro
    """
    try:
        # headers = {'Content-type': 'application/json',
        #            'Accept': 'application/json',
        #            'access-token': token}
        token = src.client_data.get("token_oking")
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization-token": "basic " + token,
        }

        url = src.client_data.get("url_api_principal") + "/api/pedido_faturar"

        jsonpickle.set_encoder_options("simplejson", use_decimal=True, sort_keys=True)
        json_invoice = jsonpickle.encode(invoice, unpicklable=False)
        # TODO ----> Melhorar solução para json_enconde com o campo amount em Decimal
        json_invoice = json_invoice.replace(
            '"valor_nf": null', f'"valor_nf":{invoice.valor_nf}'
        )
        if src.print_payloads:
            print(json_invoice)
        logger.info("LOG AUXILIAR - realizando post na Api /api/pedido_faturar")
        response = requests.post(url, json=json.loads(json_invoice), headers=headers)

        if response.ok:
            logger.info("LOG AUXILIAR - response ok, saindo")
            return None
        else:
            # jsonReturn = f'"text":{response.text}, "status_code\":{response.status_code}'
            # err = jsonpickle.decode(response.content)
            # invoice_response = InvoiceResponse(**err)
            # result = [GenericResponse(**t) for t in response.json()]
            invoice_response = response.text
            if "_okvendas" in invoice_response or "_openkuget" in invoice_response:
                invoice_response = (
                    "Erro interno no servidor. Entre em contato com o suporte"
                )
            logger.info("LOG AUXILIAR - post mal sucedido, saindo")
            return invoice_response

    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API {str(ex)}")


def post_sent_okinghub(sent):
    try:
        url = f'{src.client_data.get("url_api_principal")}/api/pedido_encaminhar'
        token = src.client_data.get("token_oking")
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization-token": "basic " + token,
        }
        json_sent = jsonpickle.encode(sent, unpicklable=False)
        if src.print_payloads:
            print(json_sent)
        response = requests.post(url, json=json.loads(json_sent), headers=headers)

        if response.ok:
            return None
        else:

            result = [GenericResponse(**t) for t in response.json()]
            invoice_response = response.text
            if "_okvendas" in invoice_response or "_openkuget" in invoice_response:
                invoice_response = (
                    "Erro interno no servidor. Entre em contato com o suporte"
                )
            return invoice_response

    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API {str(ex)}")


def post_delivered_okinghub(delivered):
    url = f'{src.client_data.get("url_api_principal")}/api/pedido_entregue'
    token = src.client_data.get("token_oking")
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization-token": "basic " + token,
    }
    jsonpickle.set_encoder_options("simplejson", use_decimal=True, sort_keys=True)
    json_delivered = jsonpickle.encode(delivered, unpicklable=False)
    if src.print_payloads:
        print(json_delivered)
    response = requests.post(url, json=json.loads(json_delivered), headers=headers)

    if response.ok:
        return None


def get_queue_order_to_duplicate():
    retorder = None
    try:
        url = f'{src.client_data.get("url_api_principal")}/api/consulta/pedido_fila_duplicar/filtros'
        token = src.client_data.get("token_oking")
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization-token": "basic " + token,
        }
        pagina = 0
        my_token = {"token": token, "pagina": pagina}
        if src.print_payloads:
            print(my_token)
        response = requests.get(url, params=my_token, headers=headers)
        if response.ok:
            retorder = [Queue(**t) for t in response.json()]
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
    except Exception as ex:
        logger.error(f"Erro ao realizar GET na api oking hub {url} - {str(ex)}")
        raise

    return retorder


def post_protocol_duplicated_order(duplicated_order):
    url = src.client_data.get("url_api_secundaria") + f"/api/pedido_duplicado_integrado"
    try:
        json_protocolos = jsonpickle.encode(duplicated_order)
        if src.print_payloads:
            print(json_protocolos)
        response = requests.post(
            url,
            json=json.loads(json_protocolos),
            headers={
                "Accept": "application/json",
                "access-token": src.client_data.get("token_api"),
            },
        )
        if response.ok:
            return True
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
            return False
    except Exception as ex:
        logger.error(
            f"Erro ao protocolar pedidos duplicados na api okvendas {url}" + str(ex),
            exc_info=True,
        )
        return False

def post_service_fees(body: List[ServiceFee]) -> List[dict]:
    """
    Envia as taxas de serviço para a API SBY.
    Args:
        body: Uma lista de objetos ServiceFee.

    Returns:
        Uma lista de dicionários para a função de validação.
    """
    try:
        url = f'{src.client_data.get("url_api_terciario")}/api/taxa_servico/'
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = {
            "access_token": src.client_data.get("token_oking"),
            "data": body
        }

        if src.print_payloads:
            logger.info(f"Enviando para API de Taxa de Serviço. URL: {url}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
        response = requests.post(url, json=payload, headers=headers)

        if response.ok:
            logger.info(f"Lote de taxas de serviço enviado com sucesso. Status: {response.status_code}")
            return [{
                "codigo_escopo": item.codigo_escopo,
                "tipo_escopo": item.tipo_escopo,
                "sucesso": True,
                "mensagem": "SUCESSO"
            } for item in body]
        else:
            error_message = f"Erro no envio do lote. Status: {response.status_code}, Resposta: {response.text}"
            logger.error(error_message)
            return [{
                "codigo_escopo": item.codigo_escopo,
                "tipo_escopo": item.tipo_escopo,
                "sucesso": False,
                "mensagem": error_message
            } for item in body]

    except requests.exceptions.RequestException as ex:
        error_message = f"Erro de conexão ao enviar taxas de serviço: {str(ex)}"
        logger.error(error_message)
        return [{
            "codigo_escopo": item.codigo_escopo,
            "tipo_escopo": item.tipo_escopo,
            "sucesso": False,
            "mensagem": error_message
        } for item in body]
    except Exception as ex:
        error_message = f"Erro inesperado ao enviar taxas de serviço: {str(ex)}"
        logger.error(error_message)
        return [{
            "codigo_escopo": item.codigo_escopo,
            "tipo_escopo": item.tipo_escopo,
            "sucesso": False,
            "mensagem": error_message
        } for item in body]


def post_generic_data(send_logs: bool, job_name: str, data: dict, api_url: str = None) -> GenericResponse:
    """
    Envia dados genéricos para API (OKING Hub ou OKVendas)
    
    Este método é usado por jobs genéricos configurados no painel.
    Detecta automaticamente o tipo de API e ajusta o formato do token:
    - OKING_HUB: Token no body como "token"
    - OKVENDAS: Token no header como "access-token"
    
    Args:
        send_logs: Flag para enviar logs
        job_name: Nome do job (ex: 'envia_comissao_job_GEN')
        data: Dicionário com dados do registro (nomes reais das colunas)
        api_url: URL customizada da API (opcional, usa url_api_principal se não fornecido)
        
    Returns:
        GenericResponse com sucesso/mensagem
        
    Exemplo:
        data = {
            "vendedor_id": "V001",
            "vendedor_nome": "João",
            "valor": 1500.00
        }
    """
    try:
        # Validar configuração
        if src.client_data is None:
            logger.error('[GENERIC API] client_data não configurado')
            return GenericResponse(
                identificador='',
                identificador2='',
                sucesso=False,
                mensagem='Configuração não carregada'
            )
        
        # Determinar URL da API
        if api_url is None:
            api_url = src.client_data.get("url_api_principal")
        
        # URL completa
        url = f'{api_url}/api/hub_processar_job_generico'
        
        # ===== DETECTAR TIPO DE API AUTOMATICAMENTE =====
        # OKING_HUB: usa "oking" no domínio e token_oking
        # OKVENDAS: usa "okvendas" no domínio e token_api_integracao
        
        is_oking_hub = 'oking' in api_url.lower() and 'okvendas' not in api_url.lower()
        
        # Preparar token baseado no tipo de API
        if is_oking_hub:
            # OKING_HUB: Token no BODY como "token"
            token = src.client_data.get("token_oking")
            if token is None:
                logger.error('[GENERIC API] Token OKING Hub não configurado')
                return GenericResponse(
                    identificador='',
                    identificador2='',
                    sucesso=False,
                    mensagem='Token OKING Hub não configurado'
                )
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # CORREÇÃO (04/11/2025): API espera "job_name", não "job"
            payload = {
                "token": token,
                "job_name": job_name,
                "dados": [data]
            }
            
            logger.debug(f'[GENERIC API] Tipo detectado: OKING_HUB (token no body)')
            
        else:
            # OKVENDAS: Token no HEADER como "access-token"
            token = src.client_data.get("token_api_integracao")
            if token is None:
                logger.error('[GENERIC API] Token OKVendas não configurado')
                return GenericResponse(
                    identificador='',
                    identificador2='',
                    sucesso=False,
                    mensagem='Token OKVendas não configurado'
                )
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "access-token": token
            }
            
            # CORREÇÃO (04/11/2025): API espera "job_name", não "job"
            payload = {
                "job_name": job_name,
                "dados": [data]
            }
            
            logger.debug(f'[GENERIC API] Tipo detectado: OKVENDAS (token no header)')
        
        # Log do payload em modo debug
        if src.print_payloads:
            logger.info(f'[GENERIC API] Enviando para {url}')
            logger.info(f'[GENERIC API] Headers: {json.dumps({k: "***" if k in ["access-token", "token"] else v for k, v in headers.items()}, indent=2)}')
            logger.info(f'[GENERIC API] Payload: {json.dumps({**payload, "token": "***"} if "token" in payload else payload, indent=2)}')
        
        # Fazer requisição
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Processar resposta
        if response.status_code == 200:
            r = response.json()
            
            # ========================================
            # CORREÇÃO (05/11/2025): API agora retorna LISTA de resultados
            # Formato: [{"identificador": "28", "identificador2": "", "sucesso": true, "mensagem": "..."}]
            # ========================================
            
            # Validar tipo de resposta
            if isinstance(r, list):
                # API retornou lista - pegar primeiro item
                if len(r) == 0:
                    logger.warning('[GENERIC API] API retornou lista vazia')
                    return GenericResponse(
                        identificador='',
                        identificador2='',
                        sucesso=False,
                        mensagem='API retornou lista vazia'
                    )
                
                # Pegar primeiro resultado da lista
                first_result = r[0]
                
                if not isinstance(first_result, dict):
                    logger.error(f'[GENERIC API] Item da lista tem tipo inválido: {type(first_result).__name__}')
                    return GenericResponse(
                        identificador='',
                        identificador2='',
                        sucesso=False,
                        mensagem=f'Tipo inválido no item da lista: {type(first_result).__name__}'
                    )
                
                # Retornar GenericResponse do primeiro item
                return GenericResponse(**first_result)
            
            elif isinstance(r, dict):
                # API retornou dict (formato antigo) - compatibilidade
                logger.debug('[GENERIC API] API retornou dict (formato antigo)')
                return GenericResponse(**r)
            
            else:
                # Tipo inválido
                logger.error(f'[GENERIC API] Resposta inválida: tipo {type(r).__name__}')
                from src.log_types import LogType
                from src.jobs.system_jobs import OnlineLogger
                OnlineLogger.send_log(
                    'post_generic_data',
                    send_logs,
                    True,
                    f'API retornou tipo inválido: {type(r).__name__}',
                    LogType.ERROR,
                    'GENERIC')
                return GenericResponse(
                    identificador='',
                    identificador2='',
                    sucesso=False,
                    mensagem=f'Tipo inválido: {type(r).__name__}'
                )
        
        else:
            # Erro HTTP
            logger.error(f'[GENERIC API] Erro HTTP {response.status_code}: {response.text}')
            from src.log_types import LogType
            from src.jobs.system_jobs import OnlineLogger
            OnlineLogger.send_log(
                'post_generic_data',
                send_logs,
                True,
                f'Erro HTTP {response.status_code}: {response.text[:200]}',
                LogType.ERROR,
                'GENERIC')
            return GenericResponse(
                identificador='',
                identificador2='',
                sucesso=False,
                mensagem=f'Erro HTTP {response.status_code}'
            )
    
    except requests.Timeout:
        logger.error('[GENERIC API] Timeout ao enviar dados genéricos')
        from src.log_types import LogType
        from src.jobs.system_jobs import OnlineLogger
        OnlineLogger.send_log(
            'post_generic_data',
            send_logs,
            True,
            'Timeout ao enviar dados (30s)',
            LogType.ERROR,
            'GENERIC')
        return GenericResponse(
            identificador='',
            identificador2='',
            sucesso=False,
            mensagem='Timeout ao enviar dados'
        )
    
    except requests.ConnectionError as e:
        logger.error(f'[GENERIC API] Erro de conexão: {str(e)}')
        from src.log_types import LogType
        from src.jobs.system_jobs import OnlineLogger
        OnlineLogger.send_log(
            'post_generic_data',
            send_logs,
            True,
            f'Erro de conexão: {str(e)}',
            LogType.ERROR,
            'GENERIC')
        return GenericResponse(
            identificador='',
            identificador2='',
            sucesso=False,
            mensagem=f'Erro de conexão: {str(e)}'
        )
    
    except Exception as e:
        logger.error(f'[GENERIC API] Erro ao enviar dados genéricos: {str(e)}')
        from src.log_types import LogType
        from src.jobs.system_jobs import OnlineLogger
        OnlineLogger.send_log(
            'post_generic_data',
            send_logs,
            True,
            f'Erro inesperado: {str(e)}',
            LogType.ERROR,
            'GENERIC')
        return GenericResponse(
            identificador='',
            identificador2='',
            sucesso=False,
            mensagem=f'Erro: {str(e)}'
        )


def post_generic_data_batch(send_logs: bool, job_name: str, data_list: list, api_url: str = None) -> dict:
    """
    Envia LOTE de dados genéricos para API (OKING Hub ou OKVendas)
    
    CORREÇÃO (05/11/2025): Implementado envio em lotes para melhor performance
    Similar aos jobs de comissão/contas a receber que já usam batching
    
    Args:
        send_logs: Flag para enviar logs
        job_name: Nome do job (ex: 'sincroniza_tipoclifor')
        data_list: LISTA de dicionários com dados dos registros
        api_url: URL customizada da API (opcional)
        
    Returns:
        dict com estatísticas:
        {
            "sucesso": bool,
            "mensagem": str,
            "total_enviado": int,
            "total_sucesso": int,
            "total_erro": int,
            "resultados": list  # Lista de GenericResponse
        }
        
    Exemplo:
        data_list = [
            {"vendedor_id": "V001", "nome": "João"},
            {"vendedor_id": "V002", "nome": "Maria"}
        ]
    """
    try:
        # Validar entrada
        if not data_list or len(data_list) == 0:
            logger.warning('[GENERIC BATCH] Lista de dados vazia')
            return {
                "sucesso": True,
                "mensagem": "Nenhum dado para enviar",
                "total_enviado": 0,
                "total_sucesso": 0,
                "total_erro": 0,
                "resultados": []
            }
        
        # Validar configuração
        if src.client_data is None:
            logger.error('[GENERIC BATCH] client_data não configurado')
            return {
                "sucesso": False,
                "mensagem": "Configuração não carregada",
                "total_enviado": len(data_list),
                "total_sucesso": 0,
                "total_erro": len(data_list),
                "resultados": []
            }
        
        # Determinar URL da API
        if api_url is None:
            api_url = src.client_data.get("url_api_principal")
        
        # URL completa
        url = f'{api_url}/api/hub_processar_job_generico'
        
        # Detectar tipo de API
        is_oking_hub = 'oking' in api_url.lower() and 'okvendas' not in api_url.lower()
        
        # Preparar token e headers
        if is_oking_hub:
            token = src.client_data.get("token_oking")
            if token is None:
                logger.error('[GENERIC BATCH] Token OKING Hub não configurado')
                return {
                    "sucesso": False,
                    "mensagem": "Token OKING Hub não configurado",
                    "total_enviado": len(data_list),
                    "total_sucesso": 0,
                    "total_erro": len(data_list),
                    "resultados": []
                }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "token": token,
                "job_name": job_name,
                "dados": data_list  # ✅ Envia LISTA completa
            }
            
        else:
            token = src.client_data.get("token_api_integracao")
            if token is None:
                logger.error('[GENERIC BATCH] Token OKVendas não configurado')
                return {
                    "sucesso": False,
                    "mensagem": "Token OKVendas não configurado",
                    "total_enviado": len(data_list),
                    "total_sucesso": 0,
                    "total_erro": len(data_list),
                    "resultados": []
                }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "access-token": token
            }
            
            payload = {
                "job_name": job_name,
                "dados": data_list  # ✅ Envia LISTA completa
            }
        
        # Log do payload em modo debug
        if src.print_payloads:
            logger.info(f'[GENERIC BATCH] Enviando {len(data_list)} registros para {url}')
            logger.info(f'[GENERIC BATCH] Headers: {json.dumps({k: "***" if k in ["access-token", "token"] else v for k, v in headers.items()}, indent=2)}')
            
            # Mostrar estrutura completa do payload (mascarando token)
            payload_log = payload.copy()
            if 'token' in payload_log:
                payload_log['token'] = '***'
            # Limitar dados mostrados
            if len(data_list) > 3:
                payload_log['dados'] = data_list[:3] + [f'... +{len(data_list)-3} registros']
            
            logger.info(f'[GENERIC BATCH] Payload completo:\n{json.dumps(payload_log, indent=2, ensure_ascii=False)}')
        
        # Fazer requisição
        logger.info(f'[GENERIC BATCH] Enviando lote de {len(data_list)} registros')
        response = requests.post(url, json=payload, headers=headers, timeout=60)  # Timeout maior para lotes
        
        # Processar resposta
        if response.status_code == 200:
            r = response.json()
            
            # API retorna lista de resultados
            if isinstance(r, list):
                resultados = []
                sucesso_count = 0
                erro_count = 0
                
                for item in r:
                    if isinstance(item, dict):
                        try:
                            gen_resp = GenericResponse(**item)
                            resultados.append(gen_resp)
                            
                            if gen_resp.sucesso:
                                sucesso_count += 1
                            else:
                                erro_count += 1
                        except Exception as e:
                            logger.error(f'[GENERIC BATCH] Erro ao processar item: {e}')
                            erro_count += 1
                
                logger.info(f'[GENERIC BATCH] Resultado: {sucesso_count} sucesso, {erro_count} erro(s)')
                
                return {
                    "sucesso": erro_count == 0,
                    "mensagem": f"{sucesso_count} sucesso, {erro_count} erro(s)",
                    "total_enviado": len(data_list),
                    "total_sucesso": sucesso_count,
                    "total_erro": erro_count,
                    "resultados": resultados
                }
            
            else:
                logger.error(f'[GENERIC BATCH] Resposta não é lista: {type(r).__name__}')
                return {
                    "sucesso": False,
                    "mensagem": f"Resposta inválida: {type(r).__name__}",
                    "total_enviado": len(data_list),
                    "total_sucesso": 0,
                    "total_erro": len(data_list),
                    "resultados": []
                }
        
        else:
            # Erro HTTP
            logger.error(f'[GENERIC BATCH] Erro HTTP {response.status_code}: {response.text}')
            return {
                "sucesso": False,
                "mensagem": f"Erro HTTP {response.status_code}",
                "total_enviado": len(data_list),
                "total_sucesso": 0,
                "total_erro": len(data_list),
                "resultados": []
            }
    
    except requests.Timeout:
        logger.error('[GENERIC BATCH] Timeout ao enviar lote')
        return {
            "sucesso": False,
            "mensagem": "Timeout ao enviar lote (60s)",
            "total_enviado": len(data_list),
            "total_sucesso": 0,
            "total_erro": len(data_list),
            "resultados": []
        }
    
    except Exception as e:
        logger.error(f'[GENERIC BATCH] Erro ao enviar lote: {str(e)}')
        return {
            "sucesso": False,
            "mensagem": f"Erro: {str(e)}",
            "total_enviado": len(data_list),
            "total_sucesso": 0,
            "total_erro": len(data_list),
            "resultados": []
        }


def post_comissoes(send_logs: bool, comissoes: list) -> dict:
    """
    Envia lote de comissões para API OKING Hub
    
    Endpoint: POST /api/hub_comissao
    Batch: Envia em lotes de até 1000 registros
    
    Args:
        send_logs: Flag para enviar logs
        comissoes: Lista de objetos Comissao
        
    Returns:
        dict com resultado do envio:
        {
            "sucesso": bool,
            "mensagem": str,
            "protocolo": str (opcional),
            "total_enviado": int,
            "total_sucesso": int,
            "total_erro": int
        }
        
    Example:
        comissoes = [Comissao(...), Comissao(...)]
        result = post_comissoes(True, comissoes)
    """
    try:
        from src.api.entities.comissao import ComissaoResponse
        from src.log_types import LogType
        from src.jobs.system_jobs import OnlineLogger
        
        # Validar token
        if src.client_data is None or src.client_data.get('token_oking') is None:
            logger.error('[COMISSAO API] Token OKING não configurado')
            OnlineLogger.send_log(
                'post_comissoes',
                send_logs,
                True,
                'Token OKING não configurado',
                LogType.ERROR,
                'COMISSAO')
            return {
                "sucesso": False,
                "mensagem": "Token não configurado",
                "total_enviado": 0,
                "total_sucesso": 0,
                "total_erro": 0
            }
        
        # URL da API
        url = f'{src.client_data.get("url_api_principal")}/api/hub_comissao'
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Converter comissões para JSON
        comissoes_json = [c.toJSON() if hasattr(c, 'toJSON') else c for c in comissoes]
        
        # Payload
        payload = {
            "token": src.client_data.get("token_oking"),
            "lista": comissoes_json
        }
        
        # Log do payload em modo debug
        if src.print_payloads:
            logger.info(f'[COMISSAO API] Enviando {len(comissoes_json)} comissões para {url}')
            logger.info(f'[COMISSAO API] Payload: {json.dumps({**payload, "token": "***"}, indent=2, default=str)}')
        
        # Fazer requisição
        logger.info(f'[COMISSAO API] Enviando lote de {len(comissoes_json)} comissões')
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        # Processar resposta
        if response.status_code == 200:
            r = response.json()

            # Se a API retornar uma lista de resultados por item (formato esperado para validação individual)
            if isinstance(r, list):
                # Agregar resultados
                total_enviado = len(comissoes_json)
                total_sucesso = 0
                for t in r:
                    try:
                        if isinstance(t, dict):
                            sucesso_val = t.get('sucesso')
                            # Aceitar: True, 1, "1", "true", "True", "SUCESSO"
                            if sucesso_val in (True, 1, '1', 'true', 'True', 'SUCESSO'):
                                total_sucesso += 1
                    except Exception:
                        continue
                total_erro = total_enviado - total_sucesso

                logger.info(f'[COMISSAO API] Lote recebido como lista de respostas ({total_enviado} itens: {total_sucesso} sucesso, {total_erro} erro)')
                if send_logs:
                    OnlineLogger.send_log(
                        'post_comissoes',
                        send_logs,
                        False,
                        f'Lote de {total_enviado} comissões enviado. Respostas individuais: {total_sucesso} sucesso(s), {total_erro} erro(s)',
                        LogType.INFO,
                        'COMISSAO')

                return {
                    "sucesso": (total_erro == 0),
                    "mensagem": 'Respostas individuais retornadas pela API',
                    "protocolo": None,
                    "total_enviado": total_enviado,
                    "total_sucesso": total_sucesso,
                    "total_erro": total_erro,
                    "response": r
                }

            # Se a API retornar um dict (protocolo / resumo)
            if isinstance(r, dict):
                logger.info(f'[COMISSAO API] Lote enviado com sucesso: {len(comissoes_json)} comissões')
                if send_logs:
                    OnlineLogger.send_log(
                        'post_comissoes',
                        send_logs,
                        False,
                        f'Lote de {len(comissoes_json)} comissões enviado com sucesso. Protocolo: {r.get("protocolo", "N/A")}',
                        LogType.INFO,
                        'COMISSAO')
                return {
                    "sucesso": True,
                    "mensagem": r.get("mensagem", "Sucesso"),
                    "protocolo": r.get("protocolo"),
                    "total_enviado": len(comissoes_json),
                    "total_sucesso": len(comissoes_json),
                    "total_erro": 0
                }

            # Tipo inesperado
            logger.error(f'[COMISSAO API] Resposta inválida: tipo {type(r).__name__}')
            OnlineLogger.send_log(
                'post_comissoes',
                send_logs,
                True,
                f'API retornou tipo inválido: {type(r).__name__}',
                LogType.ERROR,
                'COMISSAO')
            return {
                "sucesso": False,
                "mensagem": f"Tipo inválido: {type(r).__name__}",
                "total_enviado": len(comissoes_json),
                "total_sucesso": 0,
                "total_erro": len(comissoes_json)
            }
        
        else:
            # Erro HTTP
            logger.error(f'[COMISSAO API] Erro HTTP {response.status_code}: {response.text}')
            OnlineLogger.send_log(
                'post_comissoes',
                send_logs,
                True,
                f'Erro HTTP {response.status_code}: {response.text[:200]}',
                LogType.ERROR,
                'COMISSAO')
            return {
                "sucesso": False,
                "mensagem": f"Erro HTTP {response.status_code}",
                "total_enviado": len(comissoes_json),
                "total_sucesso": 0,
                "total_erro": len(comissoes_json)
            }
    
    except requests.Timeout:
        logger.error('[COMISSAO API] Timeout ao enviar comissões (60s)')
        from src.log_types import LogType
        from src.jobs.system_jobs import OnlineLogger
        OnlineLogger.send_log(
            'post_comissoes',
            send_logs,
            True,
            f'Timeout ao enviar lote de {len(comissoes)} comissões (60s)',
            LogType.ERROR,
            'COMISSAO')
        return {
            "sucesso": False,
            "mensagem": "Timeout ao enviar dados",
            "total_enviado": len(comissoes),
            "total_sucesso": 0,
            "total_erro": len(comissoes)
        }
    
    except requests.ConnectionError as e:
        logger.error(f'[COMISSAO API] Erro de conexão: {str(e)}')
        from src.log_types import LogType
        from src.jobs.system_jobs import OnlineLogger
        OnlineLogger.send_log(
            'post_comissoes',
            send_logs,
            True,
            f'Erro de conexão ao enviar {len(comissoes)} comissões: {str(e)}',
            LogType.ERROR,
            'COMISSAO')
        return {
            "sucesso": False,
            "mensagem": f"Erro de conexão: {str(e)}",
            "total_enviado": len(comissoes),
            "total_sucesso": 0,
            "total_erro": len(comissoes)
        }
    
    except Exception as e:
        logger.error(f'[COMISSAO API] Erro ao enviar comissões: {str(e)}')
        from src.log_types import LogType
        from src.jobs.system_jobs import OnlineLogger
        OnlineLogger.send_log(
            'post_comissoes',
            send_logs,
            True,
            f'Erro inesperado ao enviar {len(comissoes)} comissões: {str(e)}',
            LogType.ERROR,
            'COMISSAO')
        return {
            "sucesso": False,
            "mensagem": f"Erro: {str(e)}",
            "total_enviado": len(comissoes),
            "total_sucesso": 0,
            "total_erro": len(comissoes)
        }


def post_contas_a_receber(send_logs: bool, contas: list) -> dict:
    """
    Envia lote de contas a receber para API OKING Hub
    
    Endpoint: POST /api/hub_importar_contas_receber
    Batch: Envia em lotes configuráveis (default 1000)
    
    Args:
        send_logs: Flag para enviar logs
        contas: Lista de objetos ContasAReceber
        
    Returns:
        dict com resultado do envio:
        {
            "sucesso": bool,
            "mensagem": str,
            "protocolo": str (opcional),
            "total_enviado": int,
            "total_sucesso": int,
            "total_erro": int,
            "response": list (respostas individuais)
        }
        
    Example:
        contas = [ContasAReceber(...), ContasAReceber(...)]
        result = post_contas_a_receber(True, contas)
    """
    try:
        from src.log_types import LogType
        from src.jobs.system_jobs import OnlineLogger
        
        # Validar token
        if src.client_data is None or src.client_data.get('token_oking') is None:
            logger.error('[CONTAS_RECEBER API] Token OKING não configurado')
            OnlineLogger.send_log(
                'post_contas_a_receber',
                send_logs,
                True,
                'Token OKING não configurado',
                LogType.ERROR,
                'CONTAS_A_RECEBER')
            return {
                "sucesso": False,
                "mensagem": "Token não configurado",
                "total_enviado": 0,
                "total_sucesso": 0,
                "total_erro": 0
            }
        
        # URL da API
        url = f'{src.client_data.get("url_api_principal")}/api/hub_importar_contas_receber'
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Converter contas para JSON
        contas_json = [c.toJSON() if hasattr(c, 'toJSON') else c for c in contas]
        
        # Payload
        payload = {
            "token": src.client_data.get("token_oking"),
            "lista": contas_json
        }
        
        # Log do payload em modo debug
        if src.print_payloads:
            logger.info(f'[CONTAS_RECEBER API] Enviando {len(contas_json)} contas para {url}')
            logger.info(f'[CONTAS_RECEBER API] Payload: {json.dumps({**payload, "token": "***"}, indent=2, default=str)}')
        
        # Fazer requisição
        logger.info(f'[CONTAS_RECEBER API] Enviando lote de {len(contas_json)} contas a receber')
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        # Processar resposta
        if response.status_code == 200:
            r = response.json()

            # Se a API retornar uma lista de resultados por item (formato esperado para validação individual)
            if isinstance(r, list):
                # Agregar resultados
                total_enviado = len(contas_json)
                total_sucesso = 0
                for t in r:
                    try:
                        if isinstance(t, dict):
                            sucesso_val = t.get('sucesso')
                            # Aceitar: True, 1, "1", "true", "True", "SUCESSO"
                            if sucesso_val in (True, 1, '1', 'true', 'True', 'SUCESSO'):
                                total_sucesso += 1
                    except Exception:
                        continue
                total_erro = total_enviado - total_sucesso

                logger.info(f'[CONTAS_RECEBER API] Lote recebido como lista de respostas ({total_enviado} itens: {total_sucesso} sucesso, {total_erro} erro)')
                if send_logs:
                    OnlineLogger.send_log(
                        'post_contas_a_receber',
                        send_logs,
                        False,
                        f'Lote de {total_enviado} contas enviado. Respostas individuais: {total_sucesso} sucesso(s), {total_erro} erro(s)',
                        LogType.INFO,
                        'CONTAS_A_RECEBER')

                return {
                    "sucesso": (total_erro == 0),
                    "mensagem": 'Respostas individuais retornadas pela API',
                    "protocolo": None,
                    "total_enviado": total_enviado,
                    "total_sucesso": total_sucesso,
                    "total_erro": total_erro,
                    "response": r
                }

            # Se a API retornar um dict (protocolo / resumo)
            if isinstance(r, dict):
                logger.info(f'[CONTAS_RECEBER API] Lote enviado com sucesso: {len(contas_json)} contas')
                if send_logs:
                    OnlineLogger.send_log(
                        'post_contas_a_receber',
                        send_logs,
                        False,
                        f'Lote de {len(contas_json)} contas enviado com sucesso. Protocolo: {r.get("protocolo", "N/A")}',
                        LogType.INFO,
                        'CONTAS_A_RECEBER')
                return {
                    "sucesso": True,
                    "mensagem": r.get("mensagem", "Sucesso"),
                    "protocolo": r.get("protocolo"),
                    "total_enviado": len(contas_json),
                    "total_sucesso": len(contas_json),
                    "total_erro": 0
                }

            # Tipo inesperado
            logger.error(f'[CONTAS_RECEBER API] Resposta inválida: tipo {type(r).__name__}')
            OnlineLogger.send_log(
                'post_contas_a_receber',
                send_logs,
                True,
                f'API retornou tipo inválido: {type(r).__name__}',
                LogType.ERROR,
                'CONTAS_A_RECEBER')
            return {
                "sucesso": False,
                "mensagem": f"Tipo inválido: {type(r).__name__}",
                "total_enviado": len(contas_json),
                "total_sucesso": 0,
                "total_erro": len(contas_json)
            }
        
        else:
            # Erro HTTP
            logger.error(f'[CONTAS_RECEBER API] Erro HTTP {response.status_code}: {response.text}')
            OnlineLogger.send_log(
                'post_contas_a_receber',
                send_logs,
                True,
                f'Erro HTTP {response.status_code} ao enviar {len(contas)} contas: {response.text[:200]}',
                LogType.ERROR,
                'CONTAS_A_RECEBER')
            return {
                "sucesso": False,
                "mensagem": f"Erro HTTP {response.status_code}",
                "total_enviado": len(contas),
                "total_sucesso": 0,
                "total_erro": len(contas)
            }
    
    except requests.Timeout:
        logger.error(f'[CONTAS_RECEBER API] Timeout ao enviar {len(contas)} contas')
        from src.log_types import LogType
        from src.jobs.system_jobs import OnlineLogger
        OnlineLogger.send_log(
            'post_contas_a_receber',
            send_logs,
            True,
            f'Timeout ao enviar lote de {len(contas)} contas (60s)',
            LogType.ERROR,
            'CONTAS_A_RECEBER')
        return {
            "sucesso": False,
            "mensagem": "Timeout ao enviar dados",
            "total_enviado": len(contas),
            "total_sucesso": 0,
            "total_erro": len(contas)
        }
    
    except requests.ConnectionError as e:
        logger.error(f'[CONTAS_RECEBER API] Erro de conexão: {str(e)}')
        from src.log_types import LogType
        from src.jobs.system_jobs import OnlineLogger
        OnlineLogger.send_log(
            'post_contas_a_receber',
            send_logs,
            True,
            f'Erro de conexão ao enviar {len(contas)} contas: {str(e)}',
            LogType.ERROR,
            'CONTAS_A_RECEBER')
        return {
            "sucesso": False,
            "mensagem": f"Erro de conexão: {str(e)}",
            "total_enviado": len(contas),
            "total_sucesso": 0,
            "total_erro": len(contas)
        }
    
    except Exception as e:
        logger.error(f'[CONTAS_RECEBER API] Erro ao enviar contas: {str(e)}')
        from src.log_types import LogType
        from src.jobs.system_jobs import OnlineLogger
        OnlineLogger.send_log(
            'post_contas_a_receber',
            send_logs,
            True,
            f'Erro inesperado ao enviar {len(contas)} contas: {str(e)}',
            LogType.ERROR,
            'CONTAS_A_RECEBER')
        return {
            "sucesso": False,
            "mensagem": f"Erro: {str(e)}",
            "total_enviado": len(contas),
            "total_sucesso": 0,
            "total_erro": len(contas)
        }

