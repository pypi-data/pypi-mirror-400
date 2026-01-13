"""
⚙️ Tela de Configuração de Jobs - OKING Hub
Lista dinâmica de jobs carregados da API com editor individual
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
import json
import urllib.request
import urllib.error
from ui_components import ModernTheme, Card, ModernButton


# ==================== COMPONENTES ====================

class SQLEditor(tk.Frame):
    """Editor SQL com numeração de linhas e syntax highlighting"""
    
    def __init__(self, parent, theme=None, height=15, **kwargs):
        super().__init__(parent, bg=(theme or ModernTheme()).BG_CODE)
        self.theme = theme or ModernTheme()
        
        # Frame principal
        editor_frame = tk.Frame(self, bg=self.theme.BG_CODE)
        editor_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Numeração de linhas
        self.line_numbers = tk.Text(
            editor_frame,
            width=4,
            padx=4,
            pady=5,
            bg=self.theme.BG_CODE,
            fg=self.theme.TEXT_SECONDARY,
            font=self.theme.get_font("sm", mono=True),
            state='disabled',
            wrap='none',
            cursor='arrow'
        )
        self.line_numbers.pack(side='left', fill='y')
        
        # Área de código
        self.code_area = scrolledtext.ScrolledText(
            editor_frame,
            height=height,
            wrap='none',
            font=self.theme.get_font("sm", mono=True),
            bg=self.theme.BG_CODE,
            fg=self.theme.TEXT_CODE,
            insertbackground='white',
            selectbackground=self.theme.PRIMARY,
            relief='flat',
            padx=8,
            pady=5,
            **kwargs
        )
        self.code_area.pack(side='left', fill='both', expand=True)
        
        # Tags de syntax highlighting
        self.code_area.tag_config('keyword', foreground='#c792ea')
        self.code_area.tag_config('string', foreground='#c3e88d')
        self.code_area.tag_config('comment', foreground='#546e7a')
        self.code_area.tag_config('number', foreground='#f78c6c')
        
        # Eventos
        self.code_area.bind('<KeyRelease>', self._on_change)
        self.code_area.bind('<MouseWheel>', self._sync_scroll)
        
        self._update_line_numbers()
    
    def _on_change(self, event=None):
        """Atualiza numeração e highlighting"""
        self._update_line_numbers()
        self._highlight_syntax()
    
    def _update_line_numbers(self):
        """Atualiza numeração de linhas"""
        line_count = int(self.code_area.index('end-1c').split('.')[0])
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
    
    def _sync_scroll(self, event):
        """Sincroniza scroll entre numeração e código"""
        self.line_numbers.yview_moveto(self.code_area.yview()[0])
    
    def _highlight_syntax(self):
        """Aplica syntax highlighting SQL"""
        # Remove tags antigas
        for tag in ['keyword', 'string', 'comment', 'number']:
            self.code_area.tag_remove(tag, '1.0', 'end')
        
        code = self.code_area.get('1.0', 'end')
        
        # Keywords SQL
        keywords = r'\b(SELECT|FROM|WHERE|JOIN|INNER|LEFT|RIGHT|OUTER|ON|AND|OR|GROUP BY|ORDER BY|HAVING|LIMIT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TABLE|INDEX|VIEW|AS|IN|NOT|NULL|IS|LIKE|BETWEEN|CASE|WHEN|THEN|ELSE|END|DISTINCT|TOP|WITH|CAST|COALESCE|COUNT|SUM|AVG|MAX|MIN)\b'
        for match in re.finditer(keywords, code, re.IGNORECASE):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_area.tag_add('keyword', start, end)
        
        # Strings
        for match in re.finditer(r"'[^']*'", code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_area.tag_add('string', start, end)
        
        # Comentários
        for match in re.finditer(r'--[^\n]*', code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_area.tag_add('comment', start, end)
        
        # Números
        for match in re.finditer(r'\b\d+\b', code):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.code_area.tag_add('number', start, end)
    
    def get(self):
        """Retorna conteúdo"""
        return self.code_area.get('1.0', 'end-1c')
    
    def set(self, content):
        """Define conteúdo"""
        self.code_area.delete('1.0', 'end')
        self.code_area.insert('1.0', content)
        self._update_line_numbers()
        self._highlight_syntax()
    
    def clear(self):
        """Limpa editor"""
        self.set('')


class ToggleSwitch(tk.Canvas):
    """Switch ON/OFF customizado"""
    
    def __init__(self, parent, theme=None, callback=None):
        self.theme = theme or ModernTheme()
        self.callback = callback
        self.state = False
        
        super().__init__(
            parent,
            width=60,
            height=30,
            bg=parent['bg'],
            highlightthickness=0,
            cursor='hand2'
        )
        
        # Background
        self.bg_rect = self.create_rectangle(
            5, 5, 55, 25,
            fill='#e2e8f0',
            outline='',
            tags='bg'
        )
        
        # Circle
        self.circle = self.create_oval(
            7, 7, 23, 23,
            fill='white',
            outline='',
            tags='circle'
        )
        
        self.bind('<Button-1>', lambda e: self._toggle())
    
    def _toggle(self):
        """Alterna estado"""
        self.state = not self.state
        self._animate()
        if self.callback:
            self.callback(self.state)
    
    def _animate(self):
        """Anima transição"""
        if self.state:
            self.itemconfig(self.bg_rect, fill=self.theme.SUCCESS)
            self.coords(self.circle, 39, 7, 55, 23)
        else:
            self.itemconfig(self.bg_rect, fill='#e2e8f0')
            self.coords(self.circle, 7, 7, 23, 23)
    
    def get_state(self):
        """Retorna estado atual"""
        return self.state
    
    def set_state(self, state):
        """Define estado"""
        self.state = state
        self._animate()


# ==================== TELA PRINCIPAL ====================

class JobsScreen(tk.Frame):
    """Tela de configuração de jobs com lista dinâmica"""
    
    def __init__(self, parent, shortname=None, token_manager=None, theme=None):
        self.theme = theme if theme else ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY)
        self.shortname = shortname
        self.token_manager = token_manager
        self.jobs_data = []
        self.current_job = None
        
        self._build_ui()
        self._load_jobs_from_api()
    
    def _build_ui(self):
        """Constrói interface"""
        # Container principal - sem padding para ocupar todo o espaço
        self.main_container = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        self.main_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # PAINEL ÚNICO: Editor do Job (ocupa toda a tela)
        self.right_panel = tk.Frame(self.main_container, bg=self.theme.BG_SECONDARY)
        self.right_panel.pack(fill='both', expand=True)
        
        self._show_empty_state()
    
    def _show_empty_state(self):
        """Mostra estado vazio (sem job selecionado)"""
        # Limpar painel
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        empty_card = Card(self.right_panel, theme=self.theme)
        empty_card.pack(fill='both', expand=True)
        
        container = tk.Frame(empty_card, bg=self.theme.BG_PRIMARY)
        container.pack(expand=True, padx=40, pady=40)
        
        tk.Label(
            container,
            text="📄",
            font=self.theme.get_font("xxl"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(pady=(0, 16))
        
        tk.Label(
            container,
            text="Selecione um job no menu lateral",
            font=self.theme.get_font("lg"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack()
    
    def _load_jobs_from_api(self):
        """Carrega jobs da API"""
        try:
            # Verificar se temos token_manager
            if not self.token_manager:
                print("[WARN] JobsScreen: token_manager não fornecido, usando dados de exemplo")
                self._load_sample_jobs()
                return
            
            # Obter base_url do token_manager (suporta shortname e URL customizada)
            base_url = self.token_manager.get_base_url()
            if not base_url:
                print("[WARN] JobsScreen: base_url não configurada, usando dados de exemplo")
                self._load_sample_jobs()
                return
            
            # Obter token ativo
            active_token = self.token_manager.get_active_token()
            if not active_token:
                print("[WARN] JobsScreen: Nenhum token ativo, usando dados de exemplo")
                self._load_sample_jobs()
                return
            
            token_value = active_token.get('token', '')
            
            # Montar URL da API usando base_url (suporta URLs customizadas)
            import urllib.parse
            url = f"https://{base_url}/api/consulta/oking_hub/filtros"
            params = {"token": token_value}
            api_url = f"{url}?{urllib.parse.urlencode(params)}"
            
            print(f"[INFO] JobsScreen: Carregando jobs da API: {base_url}")
            
            # Fazer requisição
            with urllib.request.urlopen(api_url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                self.jobs_data = data.get('modulos', [])
                print(f"[INFO] JobsScreen: {len(self.jobs_data)} jobs carregados com sucesso!")
                
        except urllib.error.URLError as e:
            print(f"[ERROR] JobsScreen: Erro de conexão com API: {e}")
            messagebox.showerror(
                "Erro de Conexão",
                f"Não foi possível conectar à API:\n{str(e)}\n\nUsando dados de exemplo."
            )
            # Dados de exemplo para desenvolvimento
            self._load_sample_jobs()
        except Exception as e:
            print(f"[ERROR] JobsScreen: Erro ao carregar jobs: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Erro",
                f"Erro ao carregar jobs:\n{str(e)}\n\nUsando dados de exemplo."
            )
            self._load_sample_jobs()
    
    def _load_sample_jobs(self):
        """Carrega jobs de exemplo (fallback)"""
        self.jobs_data = [
            {
                "job": "envia_cliente_job",
                "nome_job": "Enviar Clientes para Hub",
                "ativo": "S",
                "comando_sql": "SELECT * FROM CLIENTES",
                "tempo_execucao": 30,
                "unidade_tempo": "M",
                "tamanho_pacote": 100
            },
            {
                "job": "sincroniza_estoque_job",
                "nome_job": "Sincronizar Estoque",
                "ativo": "N",
                "comando_sql": "SELECT * FROM ESTOQUE",
                "tempo_execucao": 15,
                "unidade_tempo": "M",
                "tamanho_pacote": 50
            }
        ]
    
    def _select_job(self, job, index=None):
        """Seleciona um job para edição"""
        self.current_job = {'data': job, 'index': index}
        self._show_job_editor()
    
    def _show_job_editor(self):
        """Mostra editor do job selecionado"""
        # Limpa painel direito
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        job = self.current_job['data']
        
        # Container com padding para manter espaçamento visual
        padded_container = tk.Frame(self.right_panel, bg=self.theme.BG_SECONDARY)
        padded_container.pack(fill='both', expand=True, padx=12, pady=12)
        
        # Container scrollável
        canvas = tk.Canvas(
            padded_container,
            bg=self.theme.BG_SECONDARY,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(padded_container, orient='vertical', command=canvas.yview)
        
        editor_container = tk.Frame(canvas, bg=self.theme.BG_SECONDARY)
        
        # Criar window com width vinculado ao canvas
        canvas_window = canvas.create_window((0, 0), window=editor_container, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Atualizar largura do editor_container para seguir o canvas
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        editor_container.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        # ✅ MOUSEWHEEL SCROLL - Vinculado apenas quando mouse sobre canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # HEADER
        self._build_job_header(editor_container, job)
        
        # STATUS
        self._build_job_status(editor_container, job)
        
        # SQL EDITOR
        self._build_job_sql_editor(editor_container, job)
        
        # CONFIGURAÇÕES
        self._build_job_config(editor_container, job)
        
        # AÇÕES
        self._build_job_actions(editor_container, job)
    
    def _build_job_header(self, parent, job):
        """Header do editor"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        # USAR nome_job se existir, senão usa job (compatibilidade com versões antigas)
        job_display_name = job.get('nome_job') or job.get('job', 'Job')
        
        tk.Label(
            container,
            text=f"⚙️ {job_display_name}",
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        # Botão voltar à direita
        ModernButton(
            container,
            text="← Voltar",
            variant="secondary",
            theme=self.theme,
            command=self._show_empty_state
        ).pack(side='right')
    
    def _build_job_status(self, parent, job):
        """Status do job"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        tk.Label(
            container,
            text="Status:",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 12))
        
        # Toggle switch com callback
        self.status_switch = ToggleSwitch(
            container, 
            theme=self.theme,
            callback=self._on_status_changed
        )
        self.status_switch.set_state(job.get('ativo') == 'S')
        self.status_switch.pack(side='left', padx=(0, 12))
        
        self.status_label = tk.Label(
            container,
            text="LIGADO" if job.get('ativo') == 'S' else "DESLIGADO",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.SUCCESS if job.get('ativo') == 'S' else self.theme.DANGER,
            bg=self.theme.BG_PRIMARY
        )
        self.status_label.pack(side='left')
    
    def _on_status_changed(self, is_active):
        """Callback quando status do job muda"""
        # Atualizar label
        if hasattr(self, 'status_label'):
            self.status_label.config(
                text="LIGADO" if is_active else "DESLIGADO",
                fg=self.theme.SUCCESS if is_active else self.theme.DANGER
            )
        
        # Habilitar/desabilitar botão executar
        # Nota: O botão só estará disponível se o job estiver ativo E as configurações estiverem salvas
        if hasattr(self, 'execute_btn'):
            # Job desativado = botão sempre desabilitado
            if not is_active:
                self.execute_btn.configure(state='disabled')
            # Job ativado = aviso que precisa salvar antes de executar
            else:
                # Mantém desabilitado até salvar
                self.execute_btn.configure(state='disabled')
                messagebox.showinfo(
                    "Atenção",
                    "⚠️ Para executar o job, você precisa:\n\n"
                    "1. Salvar as configurações primeiro\n"
                    "2. Depois o botão 'Executar Job' será habilitado",
                    parent=self.winfo_toplevel()
                )
    
    def _build_job_sql_editor(self, parent, job):
        """Editor SQL"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=20, pady=16)
        
        # Header com título e botão copiar
        header_frame = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        header_frame.pack(fill='x', pady=(0, 8))
        
        # Título do editor
        tk.Label(
            header_frame,
            text="📝 Query SQL:",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        # Botão Copiar Query
        ModernButton(
            header_frame,
            text="📋 Copiar",
            variant="secondary",
            theme=self.theme,
            command=self._copy_query_to_clipboard
        ).pack(side='left', padx=(8, 0))
        
        # Editor SQL (altura dinâmica baseada no estado de expansão)
        # Editor SQL com altura maior já que agora ocupa toda a tela
        self.sql_editor = SQLEditor(container, theme=self.theme, height=20)
        self.sql_editor.pack(fill='both', expand=True)
        self.sql_editor.set(job.get('comando_sql', ''))
    
    def _build_job_config(self, parent, job):
        """Configurações do job"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        tk.Label(
            container,
            text="⏱️ Configurações:",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 12))
        
        # Intervalo
        interval_frame = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        interval_frame.pack(fill='x', pady=(0, 8))
        
        tk.Label(
            interval_frame,
            text="Intervalo de execução:",
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 12))
        
        self.interval_entry = tk.Entry(
            interval_frame,
            font=self.theme.get_font("md"),
            width=10
        )
        self.interval_entry.insert(0, str(job.get('tempo_execucao', 0)))
        self.interval_entry.pack(side='left', padx=(0, 8))
        
        tk.Label(
            interval_frame,
            text="minutos",
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 12))
        
        # Label formatado (atualizado dinamicamente)
        self.interval_formatted_label = tk.Label(
            interval_frame,
            text=f"({self._format_intervalo_tempo(job.get('tempo_execucao', 0))})",
            font=self.theme.get_font("sm"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        )
        self.interval_formatted_label.pack(side='left')
        
        # Atualizar label quando o valor mudar
        def update_interval_label(event=None):
            try:
                minutos = float(self.interval_entry.get() or 0)
                formatted = self._format_intervalo_tempo(minutos)
                self.interval_formatted_label.config(text=f"({formatted})")
            except ValueError:
                self.interval_formatted_label.config(text="(valor inválido)")
        
        self.interval_entry.bind('<KeyRelease>', update_interval_label)
    
    def _build_job_actions(self, parent, job):
        """Ações do job"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        ModernButton(
            container,
            text="💾 Salvar Configuração",
            variant="primary",
            theme=self.theme,
            command=self._save_job_config
        ).pack(side='left', padx=(0, 8))
        
        # Botão Executar Job - armazenar referência
        self.execute_btn = ModernButton(
            container,
            text="▶️ Executar Job",
            variant="success",
            theme=self.theme,
            command=self._test_query
        )
        self.execute_btn.pack(side='left')
        
        # Desabilitar botão se job estiver desativado
        if self.current_job and self.current_job['data'].get('ativo') != 'S':
            self.execute_btn.configure(state='disabled')
    
    def _copy_query_to_clipboard(self):
        """Copia a query SQL completa para a área de transferência"""
        if not hasattr(self, 'sql_editor'):
            return
        
        query = self.sql_editor.get()
        
        if not query.strip():
            messagebox.showwarning(
                "Aviso",
                "A query está vazia!",
                parent=self.winfo_toplevel()
            )
            return
        
        try:
            # Remove linhas em branco duplicadas (normaliza para \n simples)
            lines = query.splitlines()
            query_clean = '\n'.join(lines)
            
            # Copiar para clipboard
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(query_clean)
            
            # Feedback visual
            messagebox.showinfo(
                "Copiado!",
                f"Query copiada para a área de transferência!\n\n"
                f"Tamanho: {len(query_clean)} caracteres\n"
                f"Linhas: {len(lines)}",
                parent=self.winfo_toplevel()
            )
            
            print(f"[INFO] JobsScreen: Query copiada para clipboard ({len(query_clean)} chars)")
        
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao copiar query:\n{str(e)}",
                parent=self.winfo_toplevel()
            )
            print(f"[ERROR] JobsScreen: Erro ao copiar query: {e}")
    
    def _save_job_config(self):
        """Salva configuração do job na API"""
        if not self.current_job:
            return
        
        job = self.current_job['data']
        
        # Verificar se temos token_manager
        if not self.token_manager:
            messagebox.showerror(
                "Erro",
                "Não é possível salvar: token manager não disponível"
            )
            return
        
        # Obter base_url
        base_url = self.token_manager.get_base_url()
        if not base_url:
            messagebox.showerror(
                "Erro",
                "Não é possível salvar: URL não configurada"
            )
            return
        
        # Obter token ativo
        active_token = self.token_manager.get_active_token()
        if not active_token:
            messagebox.showerror(
                "Erro",
                "Nenhum token ativo encontrado"
            )
            return
        
        token_value = active_token.get('token', '')
        
        # Coleta dados do formulário
        try:
            sql_comando = self.sql_editor.get()
            tempo_exec = int(self.interval_entry.get() or 0)
            status_ativo = 'S' if self.status_switch.get_state() else 'N'
            
            # Preparar payload para API
            dados = {
                'comando': sql_comando,  # JSON já faz escape automaticamente
                'intervalo': tempo_exec,
                'observacao': job.get('observacao', ''),
                'job': job.get('job'),
                'ativo': status_ativo,
                'token': token_value
            }
            
            print(f"[INFO] JobsScreen: Salvando job '{job.get('job')}'...")
            print(f"[DEBUG] Payload: {dados}")
            
            # Enviar para API usando base_url (suporta URLs customizadas)
            import urllib.request
            import json
            
            api_url = f"https://{base_url}/api/oking_atualiza_tarefa"
            
            req = urllib.request.Request(
                api_url,
                data=json.dumps(dados).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # API retorna lista, pegar primeiro item
                if isinstance(result, list) and len(result) > 0:
                    result = result[0]
                
                if result.get('sucesso'):
                    # Atualizar dados locais
                    config = {
                        'job': job.get('job'),
                        'ativo': status_ativo,
                        'comando_sql': sql_comando,
                        'tempo_execucao': tempo_exec,
                        'unidade_tempo': job.get('unidade_tempo', 'M')
                    }
                    self.jobs_data[self.current_job['index']].update(config)
                    
                    mensagem_retorno = result.get('mensagem', 'Configuração salva com sucesso')
                    print(f"[INFO] JobsScreen: {mensagem_retorno}")
                    
                    # Habilitar botão executar SE o job estiver ativo
                    if hasattr(self, 'execute_btn'):
                        if status_ativo == 'S':
                            self.execute_btn.configure(state='normal')
                            print(f"[INFO] JobsScreen: Botão 'Executar Job' HABILITADO (job ativo)")
                        else:
                            self.execute_btn.configure(state='disabled')
                            print(f"[INFO] JobsScreen: Botão 'Executar Job' DESABILITADO (job inativo)")
                    
                    # Mensagem de sucesso
                    messagebox.showinfo(
                        "Configuração Salva",
                        f"Job: {job.get('nome_job') or job.get('job')}\n"
                        f"Status: {'ATIVO ✅' if status_ativo == 'S' else 'INATIVO ❌'}\n"
                        f"Intervalo: {self._format_intervalo_tempo(tempo_exec)}"
                    )
                else:
                    mensagem_erro = result.get('mensagem', 'Erro desconhecido')
                    raise Exception(mensagem_erro)
                    
        except ValueError as e:
            messagebox.showerror(
                "Erro de Validação",
                "Intervalo deve ser um número válido"
            )
        except urllib.error.HTTPError as e:
            # Tratar erros HTTP específicos
            print(f"[ERROR] JobsScreen: HTTP {e.code} ao salvar job")
            
            try:
                error_response = json.loads(e.read().decode('utf-8'))
                if isinstance(error_response, list) and len(error_response) > 0:
                    error_response = error_response[0]
                mensagem_erro = error_response.get('mensagem', 'Erro desconhecido')
            except:
                mensagem_erro = f"Erro HTTP {e.code}"
            
            if e.code == 401:
                messagebox.showerror(
                    "Erro de Autenticação",
                    "Token inválido ou não encontrado.\nVerifique suas credenciais na tela de Tokens."
                )
            elif e.code == 400:
                messagebox.showerror(
                    "Dados Inválidos",
                    mensagem_erro
                )
            else:
                messagebox.showerror(
                    "Erro ao Salvar",
                    f"Erro HTTP {e.code}: {mensagem_erro}"
                )
        except urllib.error.URLError as e:
            print(f"[ERROR] JobsScreen: Erro de conexão ao salvar job: {e}")
            messagebox.showerror(
                "Erro de Conexão",
                "Não foi possível conectar à API"
            )
        except Exception as e:
            print(f"[ERROR] JobsScreen: Erro ao salvar job: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Erro ao Salvar",
                f"Erro ao salvar configuração: {str(e)}"
            )
    
    def _test_query(self):
        """Executa o JOB completo para testar"""
        if not self.current_job:
            messagebox.showwarning("Aviso", "Nenhum job selecionado!")
            return
        
        # Obter dados do job (estrutura: {'data': job_dict, 'index': int})
        job_data = self.current_job.get('data', {})
        job_name = job_data.get('job')
        
        if not job_name:
            messagebox.showerror("Erro", "Nome do job não encontrado!")
            return
        
        # VERIFICAR SE O JOB ESTÁ ATIVO
        if job_data.get('ativo') != 'S':
            messagebox.showwarning(
                "Job Desativado",
                "⚠️ Este job está DESATIVADO!\n\n"
                "Para executar o job você precisa:\n"
                "1. Ativar o switch de status (LIGADO)\n"
                "2. Salvar as configurações\n"
                "3. Depois o botão 'Executar Job' será habilitado",
                parent=self.winfo_toplevel()
            )
            return
        
        try:
            print(f"[INFO] JobsScreen: Executando JOB '{job_name}'...")
            
            # Importar módulos necessários
            from src import utils
            
            # Verificar se é job genérico pelo campo job_generico (não apenas se está no dict)
            is_generic = job_data.get('job_generico') == 'S'
            
            if is_generic:
                # Job Genérico - usar generic_jobs
                print(f"[INFO] JobsScreen: '{job_name}' é um job genérico")
                from src.jobs import generic_jobs
                job_function = generic_jobs.job_generic
            else:
                # Job Específico - buscar função no dict
                if job_name not in utils.dict_all_jobs:
                    messagebox.showerror(
                        "Erro",
                        f"Job '{job_name}' não encontrado!\n\n"
                        f"Certifique-se que:\n"
                        f"1. O job está implementado no código, OU\n"
                        f"2. O campo 'job_generico' está marcado como 'S' na API"
                    )
                    return
                job_function = utils.dict_all_jobs[job_name]['job_function']
            
            # Obter token ativo
            active_token = self.token_manager.get_active_token()
            if not active_token:
                messagebox.showerror("Erro", "Token ativo não encontrado!")
                return
            
            token_value = active_token.get('token', '')
            
            # Buscar dados completos da API (incluindo configurações de banco)
            # Usa base_url do token_manager (suporta URLs customizadas)
            base_url = self.token_manager.get_base_url()
            api_url = f"https://{base_url}/api/consulta/oking_hub/filtros?token={token_value}"
            
            with urllib.request.urlopen(api_url, timeout=10) as response:
                api_data = json.loads(response.read().decode('utf-8'))
            
            # Inicializar src.client_data para os jobs que dependem dele
            import src
            src.client_data = api_data
            
            # Criar job_config manualmente (igual ao modo console)
            job_config = {
                'db_host': api_data.get('host'),
                'db_port': api_data.get('port'),
                'db_user': api_data.get('user'),
                'db_type': api_data.get('db_type'),
                'db_seller': api_data.get('loja_id'),
                'db_name': api_data.get('database'),
                'db_pwd': api_data.get('password'),
                'db_client': api_data.get('diretorio_client'),
                'operacao': api_data.get('operacao'),
                'send_logs': job_data.get('send_logs', True),
                'enviar_logs': job_data.get('send_logs', True),
                'enviar_logs_debug': job_data.get('enviar_logs_debug', False),
                'job_name': job_name,
                'executar_query_semaforo': job_data.get('executar_query_semaforo', True),
                'ativo': job_data.get('ativo', 'S'),
                'sql': job_data.get('comando_sql', ''),
                'comando_sql': job_data.get('comando_sql', ''),
                'semaforo_sql': job_data.get('exists_sql', ''),
                'query_final': job_data.get('query_final', ''),
                'ultima_execucao': job_data.get('ultima_execucao'),
                'old_version': job_data.get('old_version', False),
                'tamanho_pacote': job_data.get('tamanho_pacote')
            }
            
            # Confirmar execução
            job_type = "GENÉRICO" if is_generic else "ESPECÍFICO"
            resposta = messagebox.askyesno(
                "Confirmar Execução",
                f"⚠️ ATENÇÃO ⚠️\n\n"
                f"Você está prestes a EXECUTAR o job:\n\n"
                f"'{job_name}' (Tipo: {job_type})\n\n"
                f"Esta ação irá:\n"
                f"• Conectar no banco de dados\n"
                f"• Executar a query SQL\n"
                f"• Processar e enviar os dados\n\n"
                f"Deseja continuar?"
            )
            
            if not resposta:
                print("[INFO] JobsScreen: Execução cancelada pelo usuário")
                return
            
            # Executar o job (igual ao modo console)
            print(f"[INFO] JobsScreen: Iniciando execução do job...")
            
            # Capturar resultado da execução
            execution_success = False
            error_message = None
            
            try:
                job_function(job_config)
                execution_success = True
                print(f"[INFO] JobsScreen: Job '{job_name}' executado sem exceções")
            except Exception as job_error:
                execution_success = False
                error_message = str(job_error)
                print(f"[ERROR] JobsScreen: Job '{job_name}' falhou: {job_error}")
                import traceback
                traceback.print_exc()
            
            # Mostrar resultado apropriado
            if execution_success:
                messagebox.showinfo(
                    "✅ Job Executado",
                    f"Job '{job_name}' executado com sucesso!\n\n"
                    f"Verifique os logs para detalhes da execução."
                )
            else:
                messagebox.showerror(
                    "❌ Erro na Execução",
                    f"Job '{job_name}' falhou durante a execução!\n\n"
                    f"Erro: {error_message[:200]}\n\n"
                    f"Verifique os logs para mais detalhes."
                )
            
        except ImportError as e:
            print(f"[ERROR] JobsScreen: Erro ao importar módulos: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Erro de Importação",
                f"Não foi possível importar módulos necessários:\n{str(e)}"
            )
        except KeyError as e:
            print(f"[ERROR] JobsScreen: Erro de configuração: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Erro",
                f"Configuração do job não encontrada:\n{str(e)}"
            )
        except Exception as e:
            print(f"[ERROR] JobsScreen: Erro ao executar job: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Erro ao Executar",
                f"Falha ao executar job:\n{str(e)}\n\n"
                f"Verifique os logs para mais detalhes."
            )
    
    def _validate_sql_syntax(self, query):
        """Validação básica de sintaxe SQL (fallback)"""
        query_upper = query.upper().strip()
        
        # Verificações básicas
        if not query_upper:
            messagebox.showerror("Erro", "Query está vazia!")
            return
        
        # Comandos SQL válidos
        valid_commands = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'EXEC', 'EXECUTE', 'CALL']
        
        if not any(query_upper.startswith(cmd) for cmd in valid_commands):
            messagebox.showerror(
                "Erro de Sintaxe",
                "Query deve começar com SELECT, INSERT, UPDATE, DELETE, EXEC ou CALL"
            )
            return
        
        # Verificar parênteses balanceados
        if query.count('(') != query.count(')'):
            messagebox.showwarning(
                "Aviso de Sintaxe",
                "Parênteses podem estar desbalanceados"
            )
            return
        
        messagebox.showinfo(
            "✅ Sintaxe Válida",
            "Sintaxe SQL aparenta estar correta!\n\n"
            f"Comando: {query_upper.split()[0]}\n"
            f"Tamanho: {len(query)} caracteres\n\n"
            "⚠️ Validação completa só é possível executando na API"
        )
    
    def _format_intervalo_tempo(self, minutos):
        """Formata intervalo de tempo de forma elegante"""
        if not minutos or minutos == 0:
            return "Sob demanda"
        
        # Converter para float caso venha como string
        try:
            minutos = float(minutos)
        except (ValueError, TypeError):
            return "N/A"
        
        # < 60 minutos
        if minutos < 60:
            if minutos == 1:
                return "1 minuto"
            return f"{int(minutos)} minutos"
        
        # >= 60 minutos: mostrar em horas
        horas = minutos / 60
        if horas < 24:
            if horas == 1:
                return "1 hora"
            # Se for número inteiro, não mostrar decimais
            if horas % 1 == 0:
                return f"{int(horas)} horas"
            # Se tiver decimal, mostrar 1 casa
            return f"{horas:.1f} horas"
        
        # >= 24 horas: mostrar em dias
        dias = horas / 24
        if dias < 7:
            if dias == 1:
                return "1 dia"
            if dias % 1 == 0:
                return f"{int(dias)} dias"
            return f"{dias:.1f} dias"
        
        # >= 7 dias: mostrar em semanas
        semanas = dias / 7
        if semanas < 4:
            if semanas == 1:
                return "1 semana"
            if semanas % 1 == 0:
                return f"{int(semanas)} semanas"
            return f"{semanas:.1f} semanas"
        
        # >= 4 semanas: mostrar em meses
        meses = dias / 30
        if meses < 12:
            if meses == 1:
                return "1 mês"
            if meses % 1 == 0:
                return f"{int(meses)} meses"
            return f"{meses:.1f} meses"
        
        # >= 12 meses: mostrar em anos
        anos = dias / 365
        if anos == 1:
            return "1 ano"
        if anos % 1 == 0:
            return f"{int(anos)} anos"
        return f"{anos:.1f} anos"
    
    def select_job_by_name(self, job_name):
        """Seleciona um job específico pelo nome"""
        # Verificar se jobs_data existe e tem conteúdo
        if not hasattr(self, 'jobs_data') or not self.jobs_data:
            print(f"[WARNING] JobsScreen: Lista de jobs não disponível ainda")
            return
        
        # Procurar job pelo nome
        for index, job in enumerate(self.jobs_data):
            if job.get('job') == job_name or job.get('nome_job') == job_name:
                # Selecionar o job
                self._select_job(job, index)
                
                print(f"[INFO] JobsScreen: Job '{job_name}' selecionado com sucesso")
                return
        
        print(f"[WARNING] JobsScreen: Job '{job_name}' não encontrado na lista")
