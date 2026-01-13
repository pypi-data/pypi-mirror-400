"""
First Access Modal - Modal de Primeiro Acesso
Captura shortname e primeiro token na primeira execução
"""

import tkinter as tk
from tkinter import messagebox
import requests
from ui_components import ModernTheme, Card, ModernButton


class FirstAccessModal:
    """Modal para configuração inicial (shortname e token)"""
    
    def __init__(self, parent, token_manager):
        """
        Args:
            parent: Janela pai
            token_manager: Instância do TokenManager
        """
        self.token_manager = token_manager
        self.result = None
        self.theme = ModernTheme()
        
        # Cria modal
        self.modal = tk.Toplevel(parent)
        self.modal.title("OKING HUB - Primeiro Acesso")
        self.modal.geometry("600x500")
        self.modal.configure(bg=self.theme.BG_PRIMARY)
        self.modal.transient(parent)
        self.modal.grab_set()
        
        # Centraliza
        self.modal.update_idletasks()
        x = (self.modal.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.modal.winfo_screenheight() // 2) - (500 // 2)
        self.modal.geometry(f"600x500+{x}+{y}")
        
        self._build_ui()
        
        # Impede fechamento com X
        self.modal.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _build_ui(self):
        """Constrói interface"""
        # Container principal
        container = tk.Frame(self.modal, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=32, pady=32)
        
        # Header
        header = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        header.pack(fill='x', pady=(0, 24))
        
        title = tk.Label(
            header,
            text="🚀 Bem-vindo ao OKING HUB",
            font=self.theme.get_font("xl", "bold"),
            bg=self.theme.BG_PRIMARY,
            fg=self.theme.TEXT_PRIMARY
        )
        title.pack()
        
        subtitle = tk.Label(
            header,
            text="Configure sua primeira integração",
            font=self.theme.get_font("sm"),
            bg=self.theme.BG_PRIMARY,
            fg=self.theme.TEXT_SECONDARY
        )
        subtitle.pack(pady=(8, 0))
        
        # Card com formulário
        card = Card(container, theme=self.theme)
        card.pack(fill='both', expand=True)
        
        # Passo 1: Shortname ou URL Customizada
        step1_label = tk.Label(
            card,
            text="Passo 1: Configuração de Acesso",
            font=self.theme.get_font("md", "bold"),
            bg='white',
            fg=self.theme.TEXT_PRIMARY
        )
        step1_label.pack(anchor='w', pady=(0, 8))
        
        help1 = tk.Label(
            card,
            text="Escolha uma das opções abaixo:",
            font=self.theme.get_font("sm"),
            bg='white',
            fg=self.theme.TEXT_SECONDARY
        )
        help1.pack(anchor='w', pady=(0, 12))
        
        # Frame para opções de configuração
        config_frame = tk.Frame(card, bg='white')
        config_frame.pack(fill='x', pady=(0, 8))
        
        # Opção 1: Shortname (padrão)
        self.config_mode = tk.StringVar(value='shortname')
        
        radio1_frame = tk.Frame(config_frame, bg='white')
        radio1_frame.pack(fill='x', pady=(0, 8))
        
        tk.Radiobutton(
            radio1_frame,
            text="Shortname padrão (ex: protec → protec.oking.openk.com.br)",
            variable=self.config_mode,
            value='shortname',
            font=self.theme.get_font("sm"),
            bg='white',
            fg=self.theme.TEXT_PRIMARY,
            activebackground='white',
            command=self._on_mode_change
        ).pack(anchor='w')
        
        self.shortname_entry = tk.Entry(
            card,
            font=self.theme.get_font("md"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            relief='flat',
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
            highlightcolor=self.theme.PRIMARY
        )
        self.shortname_entry.pack(fill='x', pady=(0, 12), ipady=8)
        
        # Opção 2: URL Customizada
        radio2_frame = tk.Frame(config_frame, bg='white')
        radio2_frame.pack(fill='x', pady=(0, 8))
        
        tk.Radiobutton(
            radio2_frame,
            text="URL customizada (ex: plugmartins.openk.com.br)",
            variable=self.config_mode,
            value='custom_url',
            font=self.theme.get_font("sm"),
            bg='white',
            fg=self.theme.TEXT_PRIMARY,
            activebackground='white',
            command=self._on_mode_change
        ).pack(anchor='w')
        
        self.custom_url_entry = tk.Entry(
            card,
            font=self.theme.get_font("md"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            relief='flat',
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
            highlightcolor=self.theme.PRIMARY,
            state='disabled'
        )
        self.custom_url_entry.pack(fill='x', pady=(0, 8), ipady=8)
        
        # Botão validar
        validate_btn = ModernButton(
            card,
            text="✓ Validar Configuração",
            command=self._validate_config,
            variant='secondary',
            theme=self.theme
        )
        validate_btn.pack(anchor='w', pady=(0, 24))
        
        # Status
        self.config_status = tk.Label(
            card,
            text="",
            font=self.theme.get_font("sm"),
            bg='white',
            fg=self.theme.TEXT_SECONDARY
        )
        self.config_status.pack(anchor='w', pady=(0, 16))
        
        # Separador
        separator = tk.Frame(card, bg=self.theme.BORDER, height=1)
        separator.pack(fill='x', pady=16)
        
        # Passo 2: Token
        step2_label = tk.Label(
            card,
            text="Passo 2: Informe os dados da Integração",
            font=self.theme.get_font("md", "bold"),
            bg='white',
            fg=self.theme.TEXT_PRIMARY
        )
        step2_label.pack(anchor='w', pady=(0, 8))
        
        # Nome da integração
        nome_label = tk.Label(
            card,
            text="Nome da Integração:",
            font=self.theme.get_font("md"),
            bg='white',
            fg=self.theme.TEXT_PRIMARY
        )
        nome_label.pack(anchor='w', pady=(0, 4))
        
        self.nome_entry = tk.Entry(
            card,
            font=self.theme.get_font("md"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            relief='flat',
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
            highlightcolor=self.theme.PRIMARY,
            state='disabled'
        )
        self.nome_entry.pack(fill='x', pady=(0, 12), ipady=8)
        
        # Token
        token_label = tk.Label(
            card,
            text="Token de Acesso:",
            font=self.theme.get_font("md"),
            bg='white',
            fg=self.theme.TEXT_PRIMARY
        )
        token_label.pack(anchor='w', pady=(0, 4))
        
        self.token_entry = tk.Entry(
            card,
            font=self.theme.get_font("md"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            relief='flat',
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
            highlightcolor=self.theme.PRIMARY,
            state='disabled'
        )
        self.token_entry.pack(fill='x', pady=(0, 8), ipady=8)
        
        # Status token
        self.token_status = tk.Label(
            card,
            text="",
            font=self.theme.get_font("sm"),
            bg='white',
            fg=self.theme.TEXT_SECONDARY
        )
        self.token_status.pack(anchor='w', pady=(0, 16))
        
        # Botões finais
        buttons_frame = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        buttons_frame.pack(fill='x', pady=(16, 0))
        
        cancel_btn = ModernButton(
            buttons_frame,
            text="Cancelar",
            command=self._on_cancel,
            variant='secondary',
            theme=self.theme
        )
        cancel_btn.pack(side='left')
        
        self.save_btn = ModernButton(
            buttons_frame,
            text="Salvar e Continuar",
            command=self._on_save,
            state='disabled',
            theme=self.theme
        )
        self.save_btn.pack(side='right')
        
        # Focus no shortname
        self.shortname_entry.focus()
        
        # Bind Enter
        self.shortname_entry.bind('<Return>', lambda e: self._validate_config())
        self.custom_url_entry.bind('<Return>', lambda e: self._validate_config())
        self.token_entry.bind('<Return>', lambda e: self._on_save())
    
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
        
        # Limpa status
        self.config_status.config(text="")
    
    def _validate_config(self):
        """Valida a configuração (shortname ou URL customizada)"""
        mode = self.config_mode.get()
        
        if mode == 'shortname':
            shortname = self.shortname_entry.get().strip()
            custom_url = None
            
            if not shortname:
                self.config_status.config(
                    text="❌ Informe o shortname",
                    fg='#dc3545'
                )
                return
            
            self.config_status.config(
                text="⏳ Validando shortname...",
                fg='#ffc107'
            )
        else:
            custom_url = self.custom_url_entry.get().strip()
            shortname = None
            
            if not custom_url:
                self.config_status.config(
                    text="❌ Informe a URL customizada",
                    fg='#dc3545'
                )
                return
            
            # Remove https:// ou http:// se usuário digitou
            custom_url = custom_url.replace('https://', '').replace('http://', '').strip('/')
            
            self.config_status.config(
                text="⏳ Validando URL customizada...",
                fg='#ffc107'
            )
        
        self.modal.update()
        
        # Valida usando TokenManager
        success, message = self.token_manager.validate_shortname(
            shortname if shortname else custom_url,
            custom_url=custom_url
        )
        
        if success:
            self.config_status.config(
                text=f"✅ {message}",
                fg='#28a745'
            )
            
            # Habilita campos de token
            self.nome_entry.config(state='normal')
            self.token_entry.config(state='normal')
            self.token_entry.focus()
            
            # Salva configuração temporariamente
            if custom_url:
                self.token_manager.set_base_url(custom_url)
                self.token_manager.set_shortname(None)  # Limpa shortname
            else:
                self.token_manager.set_shortname(shortname)
                self.token_manager.set_base_url(None)  # Limpa URL customizada
            
        else:
            self.config_status.config(
                text=f"❌ {message}",
                fg='#dc3545'
            )
    
    def _on_save(self):
        """Salva configurações"""
        nome = self.nome_entry.get().strip()
        token = self.token_entry.get().strip()
        
        if not nome:
            self.token_status.config(
                text="❌ Informe o nome da integração",
                fg='#dc3545'
            )
            return
        
        if not token:
            self.token_status.config(
                text="❌ Informe o token",
                fg='#dc3545'
            )
            return
        
        self.token_status.config(
            text="⏳ Validando token...",
            fg='#ffc107'
        )
        self.modal.update()
        
        # Valida token
        base_url = self.token_manager.get_base_url()
        success, message, integracao = self.token_manager.validate_token(token, base_url)
        
        if success:
            # Adiciona token
            self.token_manager.add_token(nome, token, ativo=True)
            
            self.token_status.config(
                text="✅ Token válido!",
                fg='#28a745'
            )
            
            self.result = {
                'shortname': self.token_manager.get_shortname(),
                'base_url': self.token_manager.get_base_url(),
                'nome': nome,
                'token': token,
                'integracao': integracao
            }
            
            self.modal.after(500, self.modal.destroy)
        else:
            self.token_status.config(
                text=f"❌ {message}",
                fg='#dc3545'
            )
    
    def _on_cancel(self):
        """Cancela configuração"""
        response = messagebox.askyesno(
            "Cancelar",
            "Deseja realmente cancelar?\n\nO aplicativo será fechado.",
            parent=self.modal
        )
        if response:
            self.result = None
            self.modal.destroy()
    
    def show(self):
        """Exibe o modal e aguarda resultado"""
        self.modal.wait_window()
        return self.result
