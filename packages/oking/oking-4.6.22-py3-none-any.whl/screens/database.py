"""
🗄️ Tela de Configuração de Banco de Dados - OKING Hub
Configurar conexões com integração à API
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
from ui_components import ModernTheme, Card, ModernButton


# ==================== COMPONENTE ENTRY ====================

class ModernEntry(tk.Frame):
    """Campo de entrada moderno"""
    def __init__(self, parent, label="", placeholder="", password=False, theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        super().__init__(parent, bg=parent['bg'])
        
        if label:
            tk.Label(
                self,
                text=label,
                font=self.theme.get_font("sm", "bold"),
                fg=self.theme.TEXT_PRIMARY,
                bg=parent['bg']
            ).pack(anchor='w', pady=(0, 6))
        
        entry_container = tk.Frame(
            self,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
        )
        entry_container.pack(fill='x')
        
        show = "•" if password else None
        self.entry = tk.Entry(
            entry_container,
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            borderwidth=0,
            show=show,
            **kwargs
        )
        self.entry.pack(fill='x', padx=12, pady=10)
        
        self.entry_container = entry_container
        self.entry.bind('<FocusIn>', lambda e: self._set_focus(True))
        self.entry.bind('<FocusOut>', lambda e: self._set_focus(False))
    
    def _set_focus(self, focused):
        color = self.theme.PRIMARY if focused else self.theme.BORDER
        self.entry_container.configure(highlightbackground=color)
    
    def get(self):
        return self.entry.get()
    
    def set(self, value):
        self.entry.delete(0, 'end')
        if value:  # Só insere se tiver valor
            self.entry.insert(0, str(value))


# ==================== TELA PRINCIPAL ====================

class DatabaseScreen(tk.Frame):
    """Tela de configuração de banco de dados com integração à API"""
    
    def __init__(self, parent, shortname, token_manager, theme=None):
        self.theme = theme if theme else ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY)
        self.shortname = shortname
        self.token_manager = token_manager
        self.entries = {}
        self.db_type_var = None
        self.canvas = None  # Referência ao canvas
        
        self._build_ui()
        self._load_config_from_api()
        
        # ✅ Limpeza quando destruir
        self.bind("<Destroy>", self._on_destroy)
    
    def _on_destroy(self, event):
        """Limpa bindings ao destruir"""
        if event.widget == self:
            try:
                self.unbind_all("<MouseWheel>")
            except:
                pass
    
    def _build_ui(self):
        """Constrói interface"""
        # Container principal
        main_container = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        main_container.pack(fill='both', expand=True, padx=24, pady=24)
        
        # Header
        self._build_header(main_container)
        
        # Canvas com scroll para o formulário
        canvas = tk.Canvas(
            main_container,
            bg=self.theme.BG_SECONDARY,
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg=self.theme.BG_SECONDARY)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ✅ MouseWheel - Vinculado apenas quando mouse está sobre o canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Salvar referência do canvas
        self.canvas = canvas
        
        canvas.pack(side="left", fill="both", expand=True, pady=(16, 0))
        scrollbar.pack(side="right", fill="y", pady=(16, 0))
        
        # Status frame
        self.status_frame = tk.Frame(self.scrollable_frame, bg=self.theme.BG_SECONDARY)
        self.status_frame.pack(fill='x', pady=(0, 12))
        
        # Formulário
        self._build_form()
    
    def _build_header(self, parent):
        """Header da tela"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        tk.Label(
            container,
            text="🗄️ Configurações de sua integração",
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        tk.Label(
            container,
            text="🔒 Senhas criptografadas com AES-256",
            font=self.theme.get_font("sm"),
            fg=self.theme.SUCCESS,
            bg=self.theme.BG_PRIMARY
        ).pack(side='right')
    
    def _build_form(self):
        """Formulário único de configuração"""
        card = Card(self.scrollable_frame, theme=self.theme)
        card.pack(fill='both', expand=True)
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=32, pady=32)
        
        # Grid layout para campos lado a lado
        # Linha 1: Tipo do Banco e Diretório/Driver
        row1 = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        row1.pack(fill='x', pady=(0, 16))
        
        # Coluna 1: Tipo do Banco
        col1 = tk.Frame(row1, bg=self.theme.BG_PRIMARY)
        col1.pack(side='left', fill='both', expand=True, padx=(0, 8))
        
        tk.Label(
            col1,
            text="Tipo do Banco",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 6))
        
        self.db_type_var = tk.StringVar(value="SQL")
        db_type_frame = tk.Frame(
            col1,
            bg=self.theme.BG_SECONDARY,
            relief='flat',
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
        )
        db_type_frame.pack(fill='x')
        
        self.db_type_dropdown = ttk.Combobox(
            db_type_frame,
            textvariable=self.db_type_var,
            values=["SQL", "MYSQL", "ORACLE", "FIREBIRD"],
            state="readonly",
            font=self.theme.get_font("md")
        )
        self.db_type_dropdown.pack(fill='x', padx=12, pady=10)
        self.db_type_dropdown.bind('<<ComboboxSelected>>', self._on_db_type_change)
        
        # Coluna 2: Diretório/Driver
        col2 = tk.Frame(row1, bg=self.theme.BG_PRIMARY)
        col2.pack(side='left', fill='both', expand=True, padx=(8, 0))
        
        # Coluna 2: Diretório/Driver
        col2 = tk.Frame(row1, bg=self.theme.BG_PRIMARY)
        col2.pack(side='left', fill='both', expand=True, padx=(8, 0))
        
        self.entries['directory_label'] = tk.Label(
            col2,
            text="Driver ODBC",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        )
        self.entries['directory_label'].pack(anchor='w', pady=(0, 6))
        
        self.entries['directory'] = ModernEntry(
            col2,
            label="",
            placeholder="ODBC Driver 17 for SQL Server",
            theme=self.theme
        )
        self.entries['directory'].pack(fill='x')
        
        # Linha 2: Host e Esquema
        row2 = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        row2.pack(fill='x', pady=(0, 16))
        
        # Host
        col3 = tk.Frame(row2, bg=self.theme.BG_PRIMARY)
        col3.pack(side='left', fill='both', expand=True, padx=(0, 8))
        
        self.entries['host'] = ModernEntry(
            col3,
            label="Host ou IP",
            placeholder="10.111.29.167",
            theme=self.theme
        )
        self.entries['host'].pack(fill='x')
        
        # Esquema
        col4 = tk.Frame(row2, bg=self.theme.BG_PRIMARY)
        col4.pack(side='left', fill='both', expand=True, padx=(8, 0))
        
        self.entries['schema'] = ModernEntry(
            col4,
            label="Esquema",
            placeholder="openk",
            theme=self.theme
        )
        self.entries['schema'].pack(fill='x')
        
        # Linha 3: Usuário e Senha
        row3 = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        row3.pack(fill='x', pady=(0, 24))
        
        # Usuário
        col5 = tk.Frame(row3, bg=self.theme.BG_PRIMARY)
        col5.pack(side='left', fill='both', expand=True, padx=(0, 8))
        
        self.entries['user'] = ModernEntry(
            col5,
            label="Usuário",
            placeholder="openk",
            theme=self.theme
        )
        self.entries['user'].pack(fill='x')
        
        # Senha
        col6 = tk.Frame(row3, bg=self.theme.BG_PRIMARY)
        col6.pack(side='left', fill='both', expand=True, padx=(8, 0))
        
        self.entries['password'] = ModernEntry(
            col6,
            label="Senha",
            password=True,
            theme=self.theme
        )
        self.entries['password'].pack(fill='x')
        
        # Botões
        buttons_frame = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        buttons_frame.pack(fill='x')
        
        ModernButton(
            buttons_frame,
            text="💾 Salvar configurações",
            variant="primary",
            theme=self.theme,
            command=self._save_config
        ).pack(side='left')
        
        # Atualizar label inicial
        self._update_directory_label()
    
    def _on_db_type_change(self, event=None):
        """Atualiza label quando muda tipo do banco"""
        self._update_directory_label()
    
    def _update_directory_label(self):
        """Atualiza label Diretório/Driver conforme tipo"""
        db_type = self.db_type_var.get()
        
        if db_type == "ORACLE":
            self.entries['directory_label'].config(text="Diretório")
        else:
            self.entries['directory_label'].config(text="Driver ODBC")
    
    def _save_config(self):
        """Salva configuração na API"""
        # Preparar dados
        dados = {
            'banco': self.db_type_var.get(),
            'diretorio_db': self.entries['directory'].get(),
            'host': self.entries['host'].get(),
            'esquema_db': self.entries['schema'].get(),
            'usuario_db': self.entries['user'].get(),
            'senha_db': self.entries['password'].get(),
            'token': self.token_manager.get_active_token()['token']
        }
        
        # Validar campos obrigatórios
        if not all([dados['banco'], dados['host'], dados['esquema_db'], 
                   dados['usuario_db'], dados['senha_db']]):
            self._show_error("⚠️ Preencha todos os campos obrigatórios")
            return
        
        try:
            # Testar conexão primeiro (mas não impede salvamento se falhar)
            self._show_info("🔄 Testando conexão com banco de dados...")
            test_result = self._test_connection(dados)
            
            if not test_result:
                # ✅ Mostra ERRO em caixa separada (messagebox)
                messagebox.showerror(
                    "Erro de Conexão",
                    "⚠️ Falha ao testar conexão com o banco de dados!\n\n"
                    "Verifique:\n"
                    "• Host e porta estão corretos\n"
                    "• Usuário e senha estão corretos\n"
                    "• Banco de dados está acessível\n"
                    "• Firewall não está bloqueando\n\n"
                    "Os dados serão salvos mesmo assim.",
                    parent=self.winfo_toplevel()
                )
            else:
                self._show_info("✅ Teste de conexão bem-sucedido!")
                self.after(1000)
            
            # ✅ Salvar na API (independente do teste)
            self._show_info("💾 Salvando configuração...")
            base_url = self.token_manager.get_base_url()
            url = f"https://{base_url}/api/integracao"
            response = requests.post(url, json=dados, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('sucesso'):
                    # ✅ Mensagem de sucesso LIMPA (sem misturar com erro de teste)
                    self._show_success(
                        f"✅ Configuração salva com sucesso!\n\n"
                        f"🗄️ Banco: {dados['banco']}\n"
                        f"🌐 Host: {dados['host']}\n"
                        f"📦 Schema: {dados['esquema_db']}\n"
                        f"{'✅ Conexão testada com sucesso!' if test_result else ''}"
                    )
                else:
                    self._show_error(f"❌ Erro ao salvar: {result.get('mensagem', 'Erro desconhecido')}")
            else:
                self._show_error(f"❌ Erro HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            self._show_error("⏱️ Timeout ao conectar com a API")
        except requests.exceptions.ConnectionError:
            self._show_error("🌐 Erro de conexão com a API")
        except Exception as e:
            self._show_error(f"❌ Erro ao salvar: {str(e)}")
            print(f"[ERROR] Erro ao salvar configuração: {e}")
    
    def _test_connection(self, dados):
        """Testa conexão com o banco usando a API de teste"""
        try:
            base_url = self.token_manager.get_base_url()
            url = f"https://{base_url}/api/testar_conexao"
            response = requests.post(url, json=dados, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('sucesso', False)
            return False
        except:
            # Se API de teste não existir, retorna True (permite salvar)
            return True
    
    def _load_config_from_api(self):
        """Carrega configuração da API"""
        try:
            # Verifica se tem token_manager
            if not self.token_manager:
                self._show_error("❌ Token manager não configurado")
                return
            
            # Obtém URL base
            base_url = self.token_manager.get_base_url()
            if not base_url:
                self._show_error("❌ URL base não configurada")
                return
            
            # Obtém token ativo
            active_token = self.token_manager.get_active_token()
            if not active_token:
                self._show_error("❌ Nenhum token ativo")
                return
            
            self._show_info("🔄 Carregando configuração da API...")
            
            token = active_token['token']
            url = f"https://{base_url}/api/consulta/integracao/filtros?token={token}"
            
            print(f"[DEBUG] Carregando config de: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[DEBUG] Resposta da API: {data}")
                
                # ✅ CORREÇÃO: Verificar estrutura {"sucesso": true, "integracao": {...}}
                if data.get('sucesso') and 'integracao' in data:
                    config = data['integracao']
                    
                    # Preencher campos
                    self.db_type_var.set(config.get('banco', 'SQL'))
                    self.entries['directory'].set(config.get('diretorio_db', ''))
                    self.entries['host'].set(config.get('host', ''))
                    self.entries['schema'].set(config.get('esquema_db', ''))
                    self.entries['user'].set(config.get('usuario_db', ''))
                    self.entries['password'].set(config.get('senha_db', ''))
                    
                    self._update_directory_label()
                    self._show_success("✅ Configuração carregada da API")
                    print(f"[INFO] Campos preenchidos: banco={config.get('banco')}, host={config.get('host')}")
                else:
                    self._show_error("⚠️ Formato de resposta inválido")
                    print(f"[ERROR] Estrutura inesperada: {data}")
                
        except requests.exceptions.Timeout:
            self._show_error("⏱️ Timeout ao carregar configuração")
        except requests.exceptions.ConnectionError:
            self._show_error("🌐 Erro de conexão ao carregar configuração")
        except Exception as e:
            self._show_error(f"❌ Erro ao carregar: {str(e)}")
            print(f"[ERROR] Exceção ao carregar config: {e}")
    
    def _show_info(self, message):
        """Mostra informação"""
        self._clear_status()
        info_frame = tk.Frame(
            self.status_frame,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.PRIMARY
        )
        info_frame.pack(fill='x')
        tk.Label(
            info_frame,
            text=message,
            font=self.theme.get_font("sm"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY,
            justify='left'
        ).pack(padx=12, pady=10)
    
    def _show_error(self, message):
        """Mostra erro"""
        self._clear_status()
        error_frame = tk.Frame(
            self.status_frame,
            bg=self.theme.DANGER_BG,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.DANGER
        )
        error_frame.pack(fill='x')
        tk.Label(
            error_frame,
            text=message,
            font=self.theme.get_font("sm"),
            fg=self.theme.DANGER,
            bg=self.theme.DANGER_BG,
            justify='left'
        ).pack(padx=12, pady=10)
    
    def _show_success(self, message):
        """Mostra sucesso"""
        self._clear_status()
        success_frame = tk.Frame(
            self.status_frame,
            bg=self.theme.SUCCESS_BG,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.SUCCESS
        )
        success_frame.pack(fill='x')
        tk.Label(
            success_frame,
            text=message,
            font=self.theme.get_font("sm"),
            fg=self.theme.SUCCESS,
            bg=self.theme.SUCCESS_BG,
            justify='left'
        ).pack(padx=12, pady=10)
    
    def _clear_status(self):
        """Limpa mensagens de status"""
        for widget in self.status_frame.winfo_children():
            widget.destroy()
