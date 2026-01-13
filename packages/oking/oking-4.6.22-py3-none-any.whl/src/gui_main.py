"""
GUI Main - Inicialização do Modo Gráfico do OKING Hub
Integra TokenManager, Jobs e Dashboard Moderno em Tkinter
"""
import sys
import logging
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.token_manager import TokenManager

logger = logging.getLogger(__name__)


def run_gui():
    """
    Função principal para iniciar o modo gráfico do OKING Hub.
    
    Fluxo:
    1. Verifica/carrega TokenManager
    2. Se primeiro acesso, exibe FirstAccessModal
    3. Carrega dados de jobs da API
    4. Exibe SplashScreen durante carregamento
    5. Abre Dashboard principal
    """
    import tkinter as tk
    from src.token_manager import TokenManager
    from src.ui.modals import FirstAccessModal, SplashScreen
    from main_integrated import IntegratedDashboard  # Dashboard CORRETA restaurada do Git
    from src.api import oking
    import src
    
    # ========== FASE 1: TokenManager ==========
    logger.info("Iniciando modo GUI - OKING Hub")
    
    token_manager = TokenManager()
    
    # Verificar se precisa fazer primeiro acesso
    if token_manager.needs_setup():
        logger.info("Primeiro acesso detectado - abrindo wizard de configuração")
        
        # Criar janela root temporária
        logger.info("Criando janela root temporária...")
        temp_root = tk.Tk()
        temp_root.title("OKING Hub - Configuração Inicial")
        
        # ✅ ESCONDER completamente a janela pai
        temp_root.withdraw()
        temp_root.update_idletasks()
        
        logger.info("Criando FirstAccessModal...")
        
        try:
            # Abrir modal de primeiro acesso
            modal = FirstAccessModal(
                parent=temp_root,
                token_manager=token_manager,
                on_complete=lambda shortname, token_name: _on_first_access_complete(
                    temp_root, shortname, token_name, token_manager
                )
            )
            
            logger.info("Modal criado com sucesso!")
            
            # ✅ FORÇAR MODAL PARA FRENTE E VISÍVEL
            logger.info("Forçando modal para frente...")
            modal.dialog.deiconify()  # Garantir que está visível
            modal.dialog.lift()
            modal.dialog.focus_force()
            modal.dialog.attributes('-topmost', True)
            modal.dialog.after(200, lambda: modal.dialog.attributes('-topmost', False))
            
            logger.info("Aguardando conclusão do wizard...")
            
            # Aguardar conclusão do wizard
            temp_root.wait_window(modal.dialog)
            
        except Exception as e:
            logger.error(f"Erro ao criar modal: {e}")
            import traceback
            traceback.print_exc()
            temp_root.destroy()
            sys.exit(1)
        
        # Se o modal foi cancelado, encerrar
        if token_manager.needs_setup():
            logger.warning("Configuração inicial cancelada pelo usuário")
            temp_root.destroy()
            sys.exit(0)
        
        temp_root.destroy()
    
    # ========== FASE 2: Carregar Dados ==========
    logger.info("TokenManager configurado - carregando dados do sistema")
    
    # Obter informações do token ativo
    shortname = token_manager.get_shortname()
    base_url = token_manager.get_base_url()
    active_token_data = token_manager.get_active_token()
    
    # Verificar se temos configuração válida (shortname OU base_url)
    if (not shortname and not base_url) or not active_token_data:
        logger.error("Erro: não foi possível carregar configuração do TokenManager")
        _show_error("Erro ao carregar configuração do sistema. Execute --console para reconfigurar.")
        sys.exit(1)
    
    token = active_token_data['token']
    token_name = active_token_data['nome']
    
    # Para compatibilidade, usar base_url se shortname não existir
    display_name = shortname if shortname else base_url
    logger.info(f"Token ativo: {token_name} (configuração: {display_name})")
    
    # Configurar variáveis globais do sistema (para compatibilidade)
    src.shortname_interface = shortname if shortname else base_url
    src.token_interface = token
    src.nome_token = token_name
    
    # ========== FASE 3: SplashScreen ==========
    root = tk.Tk()
    root.withdraw()  # Esconder janela principal temporariamente
    
    splash = SplashScreen(root)
    splash.update_progress(0, "Inicializando...")
    
    try:
        # Carregar jobs da API
        splash.update_progress(30, "Conectando à API...")
        
        # Buscar configuração de jobs
        try:
            # Obter URL base do token_manager
            base_url = token_manager.get_base_url()
            
            # Fazer requisição diretamente com a URL correta
            import requests
            url = f'https://{base_url}/api/consulta/oking_hub/filtros?token={token}'
            response = requests.get(url, timeout=10)
            
            splash.update_progress(50, "Carregando jobs...")
            
            if response.status_code == 200:
                jobs_config = response.json()
                loja_id = jobs_config.get('loja_id', '')
                
                # Formatar jobs para o dashboard
                jobs_data = _format_jobs_for_dashboard(jobs_config)
                
                splash.update_progress(80, "Preparando interface...")
            else:
                logger.warning("Nenhum dado de jobs retornado pela API")
                jobs_data = []
                loja_id = ""
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados da API: {e}")
            jobs_data = []
            loja_id = ""
        
        # ========== FASE 4: Dashboard ==========
        logger.info("Fase 4: Preparando Dashboard")
        splash.update_progress(90, "Abrindo dashboard...")
        
        # Fechar splash ANTES de criar o dashboard
        logger.info("Fechando splash screen...")
        splash.close()
        
        # Mostrar janela principal
        logger.info("Mostrando janela principal...")
        root.deiconify()
        root.lift()  # Trazer para frente
        root.focus_force()  # Forçar foco
        
        # Criar dashboard ORIGINAL do Git (funcionando) com parâmetros
        logger.info("Criando dashboard integrada...")
        dashboard = IntegratedDashboard(
            root=root,
            shortname=shortname,
            token_manager=token_manager,
            jobs_data=jobs_data
        )
        
        # Iniciar loop principal DIRETAMENTE
        logger.info("Dashboard inicializada com sucesso - iniciando mainloop")
        root.mainloop()  # Chamar mainloop diretamente na janela root
        
    except Exception as e:
        logger.error(f"Erro ao inicializar dashboard: {e}")
        import traceback
        traceback.print_exc()
        
        splash.close()
        _show_error(f"Erro ao inicializar interface gráfica:\n\n{str(e)}")
        sys.exit(1)


def _on_first_access_complete(root, shortname_or_url: str, token_name: str, token_manager: 'TokenManager'):
    """
    Callback executado quando o primeiro acesso é concluído
    
    Args:
        shortname_or_url: Pode ser shortname OU URL customizada
        token_name: Nome do token
        token_manager: Instância do TokenManager
    """
    logger.info(f"Primeiro acesso concluído: {shortname_or_url} / {token_name}")
    # TokenManager já foi atualizado pelo modal
    # Apenas logamos a conclusão


def _format_jobs_for_dashboard(jobs_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Formata os dados de jobs da API para o formato esperado pelo Dashboard.
    
    Args:
        jobs_config: Configuração de jobs retornada pela API
        
    Returns:
        Lista de jobs formatados para o dashboard
    """
    jobs_data = []
    
    # Mapear os jobs da configuração
    # TODO: Ajustar conforme estrutura real retornada pela API
    if 'jobs' in jobs_config:
        for job in jobs_config['jobs']:
            jobs_data.append({
                'name': job.get('job_name', 'Job Desconhecido'),
                'status': 'ativo' if job.get('ativo') == 'S' else 'inativo',
                'last_run': job.get('ultima_execucao', 'Nunca'),
                'interval': f"{job.get('intervalo', '?')} min"
            })
    
    return jobs_data


def _show_error(message: str):
    """Exibe uma mensagem de erro em um diálogo modal"""
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Erro - OKING Hub", message)
    root.destroy()


if __name__ == "__main__":
    # Permitir executar este arquivo diretamente para testes
    run_gui()
