"""
Modals - Janelas Modais para o OKING Hub
FirstAccessModal: Wizard de primeiro acesso (2 passos)
SplashScreen: Tela de carregamento
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

try:
    from src.ui.theme import ModernTheme
    from src.ui.components import ModernButton
    from src.token_manager import TokenManager
    from src.api import oking
except ImportError:
    # Fallback para testes standalone
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.ui.theme import ModernTheme
    from src.ui.components import ModernButton
    from src.token_manager import TokenManager
    from src.api import oking


class FirstAccessModal:
    """
    Modal de Primeiro Acesso - Wizard de 2 passos
    
    Passo 1: Solicitar e validar shortname
    Passo 2: Solicitar nome do token e token, validar com API
    """
    
    def __init__(self, parent, token_manager: TokenManager, on_complete: Callable):
        self.parent = parent
        self.token_manager = token_manager
        self.on_complete = on_complete
        self.theme = ModernTheme()
        
        # Estado do wizard
        self.current_step = 1
        self.shortname = ""
        self.token_name = ""
        self.token_value = ""
        
        print("[DEBUG FirstAccessModal] Iniciando construção do modal...")
        
        # Criar janela modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuração Inicial - OKING Hub")
        
        print("[DEBUG FirstAccessModal] Toplevel criado")
        
        # Configurar janela
        self._setup_window()
        
        print("[DEBUG FirstAccessModal] Window setup concluído")
        
        # Construir interface
        self._build_ui()
        
        print("[DEBUG FirstAccessModal] UI construída")
        
        # Centralizar
        self._center_window()
        
        print("[DEBUG FirstAccessModal] Janela centralizada")
        
        # ✅ SEQUÊNCIA OTIMIZADA PARA FORÇAR VISIBILIDADE
        self.dialog.withdraw()  # Primeiro esconder
        self.dialog.update_idletasks()  # Processar mudanças
        self.dialog.deiconify()  # Mostrar novamente
        self.dialog.lift()  # Trazer para frente
        self.dialog.attributes('-topmost', True)  # Sempre no topo
        self.dialog.focus_force()  # Forçar foco
        
        # Após 300ms, permitir que outras janelas fiquem na frente
        self.dialog.after(300, lambda: self.dialog.attributes('-topmost', False))
        
        print("[DEBUG FirstAccessModal] Janela forçada para frente")
        
        # Agora sim pegar o foco (modal)
        self.dialog.grab_set()
        self.dialog.transient(parent)
        
        print("[DEBUG FirstAccessModal] Modal configurado e pronto!")
        
    def _setup_window(self):
        """Configura propriedades da janela"""
        self.dialog.geometry("750x700")
        self.dialog.configure(bg=self.theme.BG_SECONDARY)
        self.dialog.resizable(True, True)  # Permitir redimensionar
        
        # Forçar atualização da geometria
        self.dialog.update_idletasks()
        
        # Não permitir fechar sem completar
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
    def _build_ui(self):
        """Constrói a interface do modal"""
        # Container principal
        main_frame = tk.Frame(self.dialog, bg=self.theme.BG_SECONDARY)
        main_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.theme.BG_SECONDARY)
        header_frame.pack(fill='x', pady=(0, 30))
        
        title_label = tk.Label(
            header_frame,
            text="🚀 Bem-vindo ao OKING Hub",
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_SECONDARY
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Vamos configurar sua conta em 2 passos simples",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_SECONDARY
        )
        subtitle_label.pack(pady=(8, 0))
        
        # Indicador de progresso
        self.progress_frame = tk.Frame(main_frame, bg=self.theme.BG_SECONDARY)
        self.progress_frame.pack(fill='x', pady=(0, 30))
        
        self._build_progress_indicator()
        
        # Container de conteúdo (troca entre passos)
        self.content_frame = tk.Frame(main_frame, bg=self.theme.BG_SECONDARY)
        self.content_frame.pack(fill='both', expand=True)
        
        # Mostrar passo 1
        self._show_step_1()
        
    def _build_progress_indicator(self):
        """Constrói indicador de progresso visual"""
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
            
        progress_container = tk.Frame(self.progress_frame, bg=self.theme.BG_SECONDARY)
        progress_container.pack()
        
        # Passo 1
        step1_color = self.theme.PRIMARY if self.current_step == 1 else self.theme.SUCCESS
        step1_label = tk.Label(
            progress_container,
            text="1",
            font=self.theme.get_font("md", "bold"),
            fg='white',
            bg=step1_color,
            width=3,
            height=1
        )
        step1_label.pack(side='left')
        
        # Linha conectora
        line = tk.Frame(progress_container, bg=self.theme.BORDER, height=2, width=50)
        line.pack(side='left', padx=10)
        
        # Passo 2
        step2_color = self.theme.PRIMARY if self.current_step == 2 else self.theme.BORDER
        step2_label = tk.Label(
            progress_container,
            text="2",
            font=self.theme.get_font("md", "bold"),
            fg='white' if self.current_step == 2 else self.theme.TEXT_SECONDARY,
            bg=step2_color,
            width=3,
            height=1
        )
        step2_label.pack(side='left')
        
    def _show_step_1(self):
        """Exibe passo 1: Configurar Shortname ou URL Customizada"""
        print("[DEBUG FirstAccessModal] Iniciando _show_step_1")
        
        try:
            # Limpar conteúdo
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            print("[DEBUG FirstAccessModal] Widgets anteriores destruídos")
            
            # Título do passo
            step_title = tk.Label(
                self.content_frame,
                text="Passo 1: Configuração de Acesso",
                font=self.theme.get_font("lg", "bold"),
                fg=self.theme.TEXT_PRIMARY,
                bg=self.theme.BG_SECONDARY
            )
            step_title.pack(pady=(0, 10))
            
            step_desc = tk.Label(
                self.content_frame,
                text="Escolha uma das opções abaixo:",
                font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY,
                bg=self.theme.BG_SECONDARY
            )
            step_desc.pack(pady=(0, 20))
            
            # Variável para modo de configuração
            self.config_mode = tk.StringVar(value='shortname')
            
            # Opção 1: Shortname padrão
            radio1_frame = tk.Frame(self.content_frame, bg=self.theme.BG_SECONDARY)
            radio1_frame.pack(fill='x', pady=(0, 10))
            
            tk.Radiobutton(
                radio1_frame,
                text="Shortname padrão (ex: protec → protec.oking.openk.com.br)",
                variable=self.config_mode,
                value='shortname',
                font=self.theme.get_font("sm"),
                bg=self.theme.BG_SECONDARY,
                fg=self.theme.TEXT_PRIMARY,
                activebackground=self.theme.BG_SECONDARY,
                selectcolor=self.theme.BG_SECONDARY,
                command=self._on_mode_change
            ).pack(anchor='w')
            
            # Campo shortname
            self.shortname_entry = tk.Entry(
                self.content_frame,
                font=self.theme.get_font("md"),
                fg=self.theme.TEXT_PRIMARY,
                bg=self.theme.BG_PRIMARY,
                relief='flat',
                bd=0,
                highlightthickness=2,
                highlightbackground=self.theme.BORDER,
                highlightcolor=self.theme.PRIMARY
            )
            self.shortname_entry.pack(fill='x', ipady=10, pady=(0, 20))
            self.shortname_entry.focus()
            
            # Opção 2: URL Customizada
            radio2_frame = tk.Frame(self.content_frame, bg=self.theme.BG_SECONDARY)
            radio2_frame.pack(fill='x', pady=(0, 10))
            
            tk.Radiobutton(
                radio2_frame,
                text="URL customizada (ex: plugmartins.openk.com.br)",
                variable=self.config_mode,
                value='custom_url',
                font=self.theme.get_font("sm"),
                bg=self.theme.BG_SECONDARY,
                fg=self.theme.TEXT_PRIMARY,
                activebackground=self.theme.BG_SECONDARY,
                selectcolor=self.theme.BG_SECONDARY,
                command=self._on_mode_change
            ).pack(anchor='w')
            
            # Campo URL customizada
            self.custom_url_entry = tk.Entry(
                self.content_frame,
                font=self.theme.get_font("md"),
                fg=self.theme.TEXT_PRIMARY,
                bg=self.theme.BG_PRIMARY,
                relief='flat',
                bd=0,
                highlightthickness=2,
                highlightbackground=self.theme.BORDER,
                highlightcolor=self.theme.PRIMARY,
                state='disabled'
            )
            self.custom_url_entry.pack(fill='x', ipady=10, pady=(0, 20))
            
            # Bind Enter key
            self.shortname_entry.bind('<Return>', lambda e: self._validate_config())
            self.custom_url_entry.bind('<Return>', lambda e: self._validate_config())
            
            # Exemplo
            example_label = tk.Label(
                self.content_frame,
                text="Exemplos: PROTEC, DEMO ou plugmartins.openk.com.br",
                font=self.theme.get_font("xs"),
                fg=self.theme.TEXT_SECONDARY,
                bg=self.theme.BG_SECONDARY,
                anchor='w'
            )
            example_label.pack(fill='x')
            
            # Botões
            button_frame = tk.Frame(self.content_frame, bg=self.theme.BG_SECONDARY)
            button_frame.pack(side='bottom', fill='x', pady=(40, 10))
            
            print("[DEBUG FirstAccessModal] Frame de botões criado")
            
            cancel_btn = ModernButton(
                button_frame,
                text="Cancelar",
                command=self._on_cancel,
                theme=self.theme,
                variant="secondary"
            )
            cancel_btn.pack(side='left')
            
            print("[DEBUG FirstAccessModal] Botão cancelar criado")
            
            next_btn = ModernButton(
                button_frame,
                text="Próximo →",
                command=self._validate_config,
                theme=self.theme
            )
            next_btn.pack(side='right')
            
            print("[DEBUG FirstAccessModal] Passo 1 construído com sucesso!")
            
        except Exception as e:
            print(f"[ERROR FirstAccessModal] Erro ao construir step 1: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _on_mode_change(self):
        """Alterna entre modo shortname e URL customizada"""
        mode = self.config_mode.get()
        
        if mode == 'shortname':
            self.shortname_entry.config(state='normal')
            self.custom_url_entry.config(state='disabled')
            self.custom_url_entry.delete(0, 'end')
            self.shortname_entry.focus()
        else:
            self.shortname_entry.config(state='disabled')
            self.shortname_entry.delete(0, 'end')
            self.custom_url_entry.config(state='normal')
            self.custom_url_entry.focus()
    
    def _validate_config(self):
        """Valida a configuração (shortname ou URL customizada)"""
        mode = self.config_mode.get()
        
        if mode == 'shortname':
            shortname = self.shortname_entry.get().strip().upper()
            custom_url = None
            
            if not shortname:
                messagebox.showwarning(
                    "Campo Obrigatório",
                    "Por favor, digite o shortname da sua empresa."
                )
                self.shortname_entry.focus()
                return
            
            # Validar formato
            if not shortname.replace('_', '').replace('-', '').isalnum():
                messagebox.showwarning(
                    "Formato Inválido",
                    "O shortname deve conter apenas letras, números, _ ou -"
                )
                self.shortname_entry.focus()
                return
        else:
            custom_url = self.custom_url_entry.get().strip()
            shortname = None
            
            if not custom_url:
                messagebox.showwarning(
                    "Campo Obrigatório",
                    "Por favor, digite a URL customizada."
                )
                self.custom_url_entry.focus()
                return
            
            # Remove https:// ou http:// se usuário digitou
            custom_url = custom_url.replace('https://', '').replace('http://', '').strip('/')
        
        # Validar com API
        try:
            logger.info(f"Validando configuração: mode={mode}, shortname={shortname}, custom_url={custom_url}")
            
            success, message = self.token_manager.validate_shortname(
                shortname if shortname else custom_url,
                custom_url=custom_url
            )
            
            if success:
                # Salvar configuração
                if custom_url:
                    self.token_manager.set_base_url(custom_url)
                    self.token_manager.set_shortname(None)
                    self.shortname = custom_url  # Para compatibilidade
                else:
                    self.token_manager.set_shortname(shortname)
                    self.token_manager.set_base_url(None)
                    self.shortname = shortname
                
                logger.info(f"Configuração validada com sucesso!")
                self.current_step = 2
                self._build_progress_indicator()
                self._show_step_2()
            else:
                messagebox.showerror(
                    "Validação Falhou",
                    f"Não foi possível validar a configuração:\n\n{message}"
                )
                
        except Exception as e:
            logger.error(f"Erro ao validar: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao validar configuração:\n\n{str(e)}"
            )
    
    def _validate_shortname(self):
        """Método mantido para compatibilidade - redireciona para _validate_config"""
        self._validate_config()
    
    def _show_step_2(self):
        """Exibe passo 2: Configurar Token"""
        # Limpar conteúdo
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Título do passo
        step_title = tk.Label(
            self.content_frame,
            text="Passo 2: Token de Acesso",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY
        )
        step_title.pack(pady=(0, 5))
        
        step_desc = tk.Label(
            self.content_frame,
            text="Configure seu token de autenticação para acessar a API",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_SECONDARY
        )
        step_desc.pack(pady=(0, 20))
        
        # Nome do token
        name_label = tk.Label(
            self.content_frame,
            text="Nome do Token:",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY,
            anchor='w'
        )
        name_label.pack(fill='x', pady=(0, 5))
        
        self.token_name_entry = tk.Entry(
            self.content_frame,
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            bd=0,
            highlightthickness=2,
            highlightbackground=self.theme.BORDER,
            highlightcolor=self.theme.PRIMARY
        )
        self.token_name_entry.pack(fill='x', ipady=8, pady=(0, 15))
        self.token_name_entry.focus()
        
        # Token
        token_label = tk.Label(
            self.content_frame,
            text="Token de Acesso:",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY,
            anchor='w'
        )
        token_label.pack(fill='x', pady=(0, 5))
        
        self.token_entry = tk.Entry(
            self.content_frame,
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            bd=0,
            highlightthickness=2,
            highlightbackground=self.theme.BORDER,
            highlightcolor=self.theme.PRIMARY,
            show="*"  # Ocultar token
        )
        self.token_entry.pack(fill='x', ipady=8, pady=(0, 8))
        
        # Bind Enter key
        self.token_entry.bind('<Return>', lambda e: self._validate_token())
        
        # Checkbox para mostrar token
        show_token_var = tk.BooleanVar()
        show_token_check = tk.Checkbutton(
            self.content_frame,
            text="Mostrar token",
            variable=show_token_var,
            command=lambda: self.token_entry.configure(show="" if show_token_var.get() else "*"),
            font=self.theme.get_font("xs"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_SECONDARY,
            activebackground=self.theme.BG_SECONDARY,
            selectcolor=self.theme.BG_PRIMARY,
            relief='flat',
            bd=0
        )
        show_token_check.pack(anchor='w')
        
        # Botões
        button_frame = tk.Frame(self.content_frame, bg=self.theme.BG_SECONDARY)
        button_frame.pack(side='bottom', fill='x', pady=(40, 10))
        
        back_btn = ModernButton(
            button_frame,
            text="← Voltar",
            command=self._go_back_to_step_1,
            theme=self.theme,
            variant="secondary"
        )
        back_btn.pack(side='left')
        
        finish_btn = ModernButton(
            button_frame,
            text="Concluir",
            command=self._validate_token,
            theme=self.theme
        )
        finish_btn.pack(side='right')
    
    def _go_back_to_step_1(self):
        """Volta para o passo 1"""
        self.current_step = 1
        self._build_progress_indicator()
        self._show_step_1()
        # Restaurar valor anterior
        self.shortname_entry.insert(0, self.shortname)
    
    def _validate_token(self):
        """Valida o token inserido"""
        token_name = self.token_name_entry.get().strip()
        token_value = self.token_entry.get().strip()
        
        if not token_name:
            messagebox.showwarning(
                "Campo Obrigatório",
                "Por favor, digite um nome para identificar este token."
            )
            self.token_name_entry.focus()
            return
        
        if not token_value:
            messagebox.showwarning(
                "Campo Obrigatório",
                "Por favor, digite o token de acesso."
            )
            self.token_entry.focus()
            return
        
        # Validar token com API
        try:
            logger.info(f"Validando token: {token_name}")
            
            # Usar validate_token do TokenManager que já usa get_base_url()
            base_url = self.token_manager.get_base_url()
            success, message, integracao = self.token_manager.validate_token(token_value, base_url)
            
            if not success:
                raise Exception(message)
            
            # Token válido! Salvar no TokenManager
            self.token_manager.add_token(
                nome=token_name,
                token=token_value,
                ativo=True
            )
            
            logger.info("Token validado e salvo com sucesso")
            
            # Chamar callback de conclusão
            self.on_complete(self.shortname, token_name)
            
            # Fechar modal
            self.dialog.destroy()
            
        except Exception as e:
            logger.error(f"Erro ao validar token: {e}")
            messagebox.showerror(
                "Token Inválido",
                f"Não foi possível validar o token.\n\n"
                f"Erro: {str(e)}\n\n"
                "Verifique se o token está correto e tente novamente."
            )
            self.token_entry.focus()
    
    def _on_cancel(self):
        """Cancela a configuração inicial"""
        result = messagebox.askyesno(
            "Cancelar Configuração",
            "Deseja realmente cancelar a configuração inicial?\n\n"
            "A aplicação será encerrada."
        )
        
        if result:
            self.dialog.destroy()
    
    def _center_window(self):
        """Centraliza a janela na tela"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')


class SplashScreen:
    """
    Splash Screen - Tela de carregamento inicial
    Exibe progresso enquanto carrega dados da aplicação
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.theme = ModernTheme()
        
        # Criar janela splash
        self.splash = tk.Toplevel(parent)
        self.splash.title("")
        self.splash.overrideredirect(True)  # Sem bordas
        
        # Configurar
        self._setup_window()
        self._build_ui()
        self._center_window()
        
        # Mostrar
        self.splash.lift()
        self.splash.update()
    
    def _setup_window(self):
        """Configura a janela"""
        self.splash.geometry("400x250")
        self.splash.configure(bg=self.theme.BG_PRIMARY)
    
    def _build_ui(self):
        """Constrói interface"""
        # Logo/Título
        title_label = tk.Label(
            self.splash,
            text="🚀 OKING Hub",
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        )
        title_label.pack(pady=(50, 10))
        
        version_label = tk.Label(
            self.splash,
            text="Carregando...",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        )
        version_label.pack()
        
        # Barra de progresso
        self.progress = ttk.Progressbar(
            self.splash,
            orient='horizontal',
            length=300,
            mode='determinate'
        )
        self.progress.pack(pady=(30, 10))
        
        # Mensagem de status
        self.status_label = tk.Label(
            self.splash,
            text="Inicializando...",
            font=self.theme.get_font("xs"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        )
        self.status_label.pack()
    
    def update_progress(self, value: int, message: str = ""):
        """Atualiza o progresso da splash screen"""
        self.progress['value'] = value
        if message:
            self.status_label.configure(text=message)
        self.splash.update()
    
    def close(self):
        """Fecha a splash screen"""
        self.splash.destroy()
    
    def _center_window(self):
        """Centraliza na tela"""
        self.splash.update_idletasks()
        width = self.splash.winfo_width()
        height = self.splash.winfo_height()
        x = (self.splash.winfo_screenwidth() // 2) - (width // 2)
        y = (self.splash.winfo_screenheight() // 2) - (height // 2)
        self.splash.geometry(f'{width}x{height}+{x}+{y}')


# ========== Testes ==========

if __name__ == "__main__":
    # Teste do FirstAccessModal
    def on_complete(shortname, token_name):
        print(f"Configuração completa: {shortname} / {token_name}")
    
    root = tk.Tk()
    root.withdraw()
    
    from src.token_manager import TokenManager
    tm = TokenManager()
    
    modal = FirstAccessModal(root, tm, on_complete)
    root.wait_window(modal.dialog)
    
    print("Modal fechado")
