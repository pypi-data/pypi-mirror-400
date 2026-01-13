"""
📋 Tela de Logs - OKING Hub
Interface moderna em Tkinter para visualizar e filtrar logs da API
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import json
import urllib.request
import urllib.error
import urllib.parse
import csv

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from ui_components import ModernTheme, Card, ModernButton, StatusBadge
from src.utils import dict_all_jobs  # Importar dicionário de jobs


# ==================== COMPONENTES ====================

class ModernTable(tk.Frame):
    """Tabela moderna com cores alternadas e hover"""
    
    def __init__(self, parent, columns=None, theme=None, on_row_click=None):
        super().__init__(parent, bg=(theme or ModernTheme()).BG_PRIMARY)
        self.theme = theme or ModernTheme()
        self.columns = columns or []
        self.on_row_click = on_row_click
        self.rows = []
        self.row_widgets = []
        
        # Frame para canvas e scrollbar vertical
        top_frame = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        top_frame.pack(fill='both', expand=True)
        
        # Canvas e scrollbars
        self.canvas = tk.Canvas(top_frame, bg=self.theme.BG_PRIMARY, highlightthickness=0)
        self.scrollbar_v = ttk.Scrollbar(top_frame, orient='vertical', command=self.canvas.yview)
        self.scrollbar_h = ttk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.table_frame = tk.Frame(self.canvas, bg=self.theme.BG_PRIMARY)
        
        self.table_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.table_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set)
        
        # Pack canvas e scrollbar vertical lado a lado
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar_v.pack(side='right', fill='y')
        
        # Pack scrollbar horizontal embaixo, após o top_frame (ocupa toda a largura do grid)
        self.scrollbar_h.pack(side='bottom', fill='x')
        
        # Configurar scroll com mousewheel
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Criar header
        self._create_header()
    
    def _create_header(self):
        header = tk.Frame(self.table_frame, bg=self.theme.PRIMARY, height=45)
        header.pack(fill='x')
        
        for i, col in enumerate(self.columns):
            label = tk.Label(
                header,
                text=col['title'],
                font=self.theme.get_font("sm", "bold"),
                fg='white',
                bg=self.theme.PRIMARY,
                anchor='w',
                padx=16,
                pady=12
            )
            label.pack(side='left', fill='both', expand=True if col.get('flex') else False)
            
            if not col.get('flex'):
                label.configure(width=col.get('width', 15))
    
    def add_row(self, data, row_data=None):
        """Adiciona uma linha à tabela"""
        row_index = len(self.rows)
        bg_color = self.theme.BG_PRIMARY if row_index % 2 == 0 else self.theme.BG_SECONDARY
        
        row_frame = tk.Frame(self.table_frame, bg=bg_color, cursor='hand2')
        row_frame.pack(fill='x')
        
        # Bind de eventos
        def on_enter(e):
            row_frame.configure(bg=self.theme.BG_HOVER)
            for child in row_frame.winfo_children():
                child.configure(bg=self.theme.BG_HOVER)
        
        def on_leave(e):
            row_frame.configure(bg=bg_color)
            for child in row_frame.winfo_children():
                if not isinstance(child, StatusBadge):
                    child.configure(bg=bg_color)
        
        def on_click(e):
            if self.on_row_click:
                self.on_row_click(row_data or data)
        
        row_frame.bind('<Enter>', on_enter)
        row_frame.bind('<Leave>', on_leave)
        row_frame.bind('<Button-1>', on_click)
        
        # Adicionar células
        for i, col in enumerate(self.columns):
            value = data[i] if i < len(data) else ""
            
            if col.get('type') == 'badge':
                # Badge de status
                status_map = {
                    'success': 'success',
                    'sucesso': 'success',
                    'warning': 'warning',
                    'aviso': 'warning',
                    'error': 'error',
                    'erro': 'error',
                }
                status = status_map.get(str(value).lower(), 'info')
                
                badge_container = tk.Frame(row_frame, bg=bg_color)
                badge_container.pack(side='left', fill='both', padx=16, pady=8)
                badge_container.bind('<Enter>', on_enter)
                badge_container.bind('<Leave>', on_leave)
                badge_container.bind('<Button-1>', on_click)
                
                badge = StatusBadge(badge_container, text=str(value), status=status, theme=self.theme)
                badge.pack()
                badge.bind('<Button-1>', on_click)
            else:
                # Label normal
                cell = tk.Label(
                    row_frame,
                    text=str(value),
                    font=self.theme.get_font("sm"),
                    fg=self.theme.TEXT_PRIMARY,
                    bg=bg_color,
                    anchor='w',
                    padx=16,
                    pady=12
                )
                cell.pack(side='left', fill='both', expand=True if col.get('flex') else False)
                cell.bind('<Enter>', on_enter)
                cell.bind('<Leave>', on_leave)
                cell.bind('<Button-1>', on_click)
                
                if not col.get('flex'):
                    cell.configure(width=col.get('width', 15))
        
        self.rows.append(data)
        self.row_widgets.append(row_frame)
    
    def clear(self):
        """Limpa todas as linhas"""
        for widget in self.row_widgets:
            widget.destroy()
        self.rows = []
        self.row_widgets = []


class Pagination(tk.Frame):
    """Componente de paginação"""
    
    def __init__(self, parent, total_pages=1, current_page=1, on_page_change=None, theme=None):
        self.theme = theme or ModernTheme()
        super().__init__(parent, bg=self.theme.BG_PRIMARY)
        
        self.total_pages = total_pages
        self.current_page = current_page
        self.on_page_change = on_page_change
        
        self._build()
    
    def _build(self):
        # Limpar widgets anteriores
        for widget in self.winfo_children():
            widget.destroy()
        
        # Container
        container = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        container.pack()
        
        # Botão Anterior
        prev_btn = tk.Button(
            container,
            text="← Anterior",
            font=self.theme.get_font("sm"),
            bg=self.theme.BG_TERTIARY if self.current_page > 1 else self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY if self.current_page > 1 else self.theme.TEXT_TERTIARY,
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2' if self.current_page > 1 else 'arrow',
            state='normal' if self.current_page > 1 else 'disabled',
            command=lambda: self._change_page(self.current_page - 1)
        )
        prev_btn.pack(side='left', padx=(0, 8))
        
        # Números de página
        start = max(1, self.current_page - 2)
        end = min(self.total_pages, start + 4)
        
        if end - start < 4:
            start = max(1, end - 4)
        
        for i in range(start, end + 1):
            is_current = i == self.current_page
            
            page_btn = tk.Button(
                container,
                text=str(i),
                font=self.theme.get_font("sm", "bold" if is_current else "normal"),
                bg=self.theme.PRIMARY if is_current else self.theme.BG_TERTIARY,
                fg='white' if is_current else self.theme.TEXT_PRIMARY,
                relief='flat',
                width=3,
                cursor='hand2' if not is_current else 'arrow',
                command=lambda p=i: self._change_page(p)
            )
            page_btn.pack(side='left', padx=2)
        
        # Botão Próximo
        next_btn = tk.Button(
            container,
            text="Próximo →",
            font=self.theme.get_font("sm"),
            bg=self.theme.BG_TERTIARY if self.current_page < self.total_pages else self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY if self.current_page < self.total_pages else self.theme.TEXT_TERTIARY,
            relief='flat',
            padx=12,
            pady=6,
            cursor='hand2' if self.current_page < self.total_pages else 'arrow',
            state='normal' if self.current_page < self.total_pages else 'disabled',
            command=lambda: self._change_page(self.current_page + 1)
        )
        next_btn.pack(side='left', padx=(8, 0))
    
    def _change_page(self, new_page):
        if 1 <= new_page <= self.total_pages and new_page != self.current_page:
            self.current_page = new_page
            self._build()
            if self.on_page_change:
                self.on_page_change(new_page)
    
    def update_pagination(self, total_pages, current_page):
        self.total_pages = total_pages
        self.current_page = current_page
        self._build()


# ==================== TELA PRINCIPAL ====================

class ToastNotification(tk.Toplevel):
    """Notificação toast suave"""
    
    def __init__(self, parent, message, duration=2000, theme=None):
        super().__init__(parent)
        self.theme = theme or ModernTheme()
        
        # Configurar janela
        self.overrideredirect(True)  # Sem bordas
        self.attributes('-topmost', True)  # Sempre no topo
        
        # Container
        container = tk.Frame(
            self,
            bg=self.theme.SUCCESS,
            relief='flat',
            borderwidth=0
        )
        container.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Ícone e mensagem
        content = tk.Frame(container, bg=self.theme.SUCCESS)
        content.pack(padx=16, pady=12)
        
        tk.Label(
            content,
            text="✓",
            font=self.theme.get_font("lg", "bold"),
            fg='white',
            bg=self.theme.SUCCESS
        ).pack(side='left', padx=(0, 8))
        
        tk.Label(
            content,
            text=message,
            font=self.theme.get_font("sm", "bold"),
            fg='white',
            bg=self.theme.SUCCESS
        ).pack(side='left')
        
        # Posicionar no canto superior direito
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        x = screen_width - self.winfo_width() - 40
        y = 80
        self.geometry(f"+{x}+{y}")
        
        # Efeito de fade in
        self.attributes('-alpha', 0.0)
        self._fade_in()
        
        # Auto-fechar
        self.after(duration, self._fade_out)
    
    def _fade_in(self, alpha=0.0):
        """Efeito fade in"""
        alpha += 0.1
        if alpha <= 1.0:
            self.attributes('-alpha', alpha)
            self.after(30, lambda: self._fade_in(alpha))
    
    def _fade_out(self, alpha=1.0):
        """Efeito fade out"""
        alpha -= 0.1
        if alpha >= 0.0:
            self.attributes('-alpha', alpha)
            self.after(30, lambda: self._fade_out(alpha))
        else:
            self.destroy()


class LogsScreen(tk.Frame):
    """Tela de visualização de logs com integração à API"""
    
    def __init__(self, parent, shortname=None, token_manager=None, theme=None):
        self.theme = theme if theme else ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY)
        
        # Configuração da API
        self.shortname = shortname
        self.token_manager = token_manager
        
        # Dados
        self.all_logs = []
        self.filtered_logs = []
        self.current_page = 1
        self.logs_per_page = 20
        
        # Referências para widgets que precisam ser atualizados
        self.stats_card = None
        self.stats_labels = {}  # Dicionário para armazenar labels de stats
        self.job_combo = None  # Referência ao combo de jobs
        
        # Auto-refresh
        self.auto_refresh_enabled = False
        self.auto_refresh_interval = 30000  # 30 segundos
        self.refresh_job = None
        
        # Filtros
        self.filter_job = tk.StringVar(value="Todos")
        self.filter_status = tk.StringVar(value="Todos")
        self.filter_date = tk.StringVar(value="Todos")
        self.search_var = tk.StringVar()
        
        self._build_ui()
        self._load_logs_from_api()
    
    def set_filters(self, status=None, date=None, job=None):
        """Define filtros externos e aplica automaticamente"""
        if status:
            self.filter_status.set(status)
        if date:
            self.filter_date.set(date)
        if job:
            self.filter_job.set(job)
        
        # Recarregar logs com os novos filtros
        self._load_logs_from_api()
    
    def _build_ui(self):
        # Canvas com scroll
        self.canvas = tk.Canvas(self, bg=self.theme.BG_SECONDARY, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.theme.BG_SECONDARY)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Vincular evento de scroll do mouse ao canvas e frame
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        
        # Vincular evento para todos os widgets filhos dinamicamente
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)
        
        # Aplicar recursivamente após construir interface
        self.after(100, lambda: bind_mousewheel(self.scrollable_frame))
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Header com título e ações
        self._build_header()
        
        # Filtros
        self._build_filters()
        
        # Popular combo de jobs com os jobs do sistema
        self._update_job_combo()
        
        # Estatísticas
        self._build_stats()
        
        # Tabela de logs
        self._build_logs_table()
        
        # Paginação
        self._build_pagination()
    
    def _build_header(self):
        header = Card(self.scrollable_frame, theme=self.theme)
        header.pack(fill='x', padx=24, pady=24)
        header.add_padding(20)
        
        container = tk.Frame(header, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x')
        
        # Título
        tk.Label(
            container,
            text="📋 Logs de Execução",
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        # Botões de ação
        actions = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        actions.pack(side='right')
        
        # Auto-refresh toggle
        self.auto_refresh_btn = ModernButton(
            actions,
            text="🔄 Auto-refresh OFF",
            variant="secondary",
            theme=self.theme,
            command=self._toggle_auto_refresh
        )
        self.auto_refresh_btn.pack(side='left', padx=(0, 8))
        
        ModernButton(
            actions,
            text="🔄 Atualizar Agora",
            variant="primary",
            theme=self.theme,
            command=self._refresh_logs
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            actions,
            text="📥 Exportar",
            variant="secondary",
            theme=self.theme,
            command=self._export_logs
        ).pack(side='left')
    
    def _build_filters(self):
        filters_card = Card(self.scrollable_frame, theme=self.theme)
        filters_card.pack(fill='x', padx=24, pady=(0, 16))
        filters_card.add_padding(20)
        
        # Título
        tk.Label(
            filters_card,
            text="🔍 Filtros",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x', pady=(0, 12))
        
        # Container de filtros
        filters_container = tk.Frame(filters_card, bg=self.theme.BG_PRIMARY)
        filters_container.pack(fill='x')
        
        # Job
        job_frame = tk.Frame(filters_container, bg=self.theme.BG_PRIMARY)
        job_frame.pack(side='left', padx=(0, 16))
        
        tk.Label(job_frame, text="Job:", font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY, bg=self.theme.BG_PRIMARY).pack(anchor='w')
        
        self.job_combo = ttk.Combobox(
            job_frame,
            textvariable=self.filter_job,
            values=["Todos"],  # Será populado dinamicamente
            width=25,
            state='readonly'
        )
        self.job_combo.pack()
        
        # Status
        status_frame = tk.Frame(filters_container, bg=self.theme.BG_PRIMARY)
        status_frame.pack(side='left', padx=(0, 16))
        
        tk.Label(status_frame, text="Status:", font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY, bg=self.theme.BG_PRIMARY).pack(anchor='w')
        
        status_combo = ttk.Combobox(
            status_frame,
            textvariable=self.filter_status,
            values=["Todos", "Sucesso", "Aviso", "Erro"],
            width=15,
            state='readonly'
        )
        status_combo.pack()
        
        # Data
        date_frame = tk.Frame(filters_container, bg=self.theme.BG_PRIMARY)
        date_frame.pack(side='left', padx=(0, 16))
        
        tk.Label(date_frame, text="Período:", font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY, bg=self.theme.BG_PRIMARY).pack(anchor='w')
        
        date_combo = ttk.Combobox(
            date_frame,
            textvariable=self.filter_date,
            values=["Hoje", "Últimos 7 dias", "Últimos 30 dias", "Todos"],
            width=18,
            state='readonly'
        )
        date_combo.pack()
        
        # Busca
        search_frame = tk.Frame(filters_container, bg=self.theme.BG_PRIMARY)
        search_frame.pack(side='left', padx=(0, 16))
        
        tk.Label(search_frame, text="Buscar:", font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY, bg=self.theme.BG_PRIMARY).pack(anchor='w')
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=self.theme.get_font("sm"),
            width=25,
            bg=self.theme.BG_TERTIARY,
            fg=self.theme.TEXT_PRIMARY,
            relief='flat',
            borderwidth=0
        )
        search_entry.pack(ipady=4)
        
        # Botão Consultar (busca na API com filtros)
        ModernButton(
            filters_container,
            text="🔍 Consultar",
            variant="primary",
            theme=self.theme,
            command=self._load_logs_from_api
        ).pack(side='left')
    
    def _build_stats(self):
        # Se já existe, apenas atualizar valores
        if self.stats_card is not None and self.stats_card.winfo_exists():
            self._update_stats_values()
            return
        
        self.stats_card = Card(self.scrollable_frame, theme=self.theme)
        self.stats_card.pack(fill='x', padx=24, pady=(0, 16))
        self.stats_card.add_padding(20)
        
        container = tk.Frame(self.stats_card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x')
        
        # Calcular estatísticas
        total = len(self.filtered_logs)
        success = sum(1 for log in self.filtered_logs if log['status'].lower() == 'sucesso')
        warning = sum(1 for log in self.filtered_logs if log['status'].lower() == 'aviso')
        error = sum(1 for log in self.filtered_logs if log['status'].lower() == 'erro')
        
        # Exibir stats
        stats = [
            ("total", "Total de Logs", total, self.theme.INFO),
            ("success", "✓ Sucessos", success, self.theme.SUCCESS),
            ("warning", "⚠ Avisos", warning, self.theme.WARNING),
            ("error", "✗ Erros", error, self.theme.DANGER),
        ]
        
        for i, (key, label, value, color) in enumerate(stats):
            stat_frame = tk.Frame(container, bg=self.theme.BG_PRIMARY)
            stat_frame.pack(side='left', padx=(0, 32 if i < len(stats)-1 else 0))
            
            tk.Label(
                stat_frame,
                text=label,
                font=self.theme.get_font("xs"),
                fg=self.theme.TEXT_SECONDARY,
                bg=self.theme.BG_PRIMARY
            ).pack()
            
            value_label = tk.Label(
                stat_frame,
                text=str(value),
                font=self.theme.get_font("xl", "bold"),
                fg=color,
                bg=self.theme.BG_PRIMARY
            )
            value_label.pack()
            
            # Salvar referência ao label de valor
            self.stats_labels[key] = value_label
    
    def _update_stats_values(self):
        """Atualiza apenas os valores das estatísticas sem recriar widgets"""
        try:
            # Calcular estatísticas
            total = len(self.filtered_logs)
            success = sum(1 for log in self.filtered_logs if log['status'].lower() == 'sucesso')
            warning = sum(1 for log in self.filtered_logs if log['status'].lower() == 'aviso')
            error = sum(1 for log in self.filtered_logs if log['status'].lower() == 'erro')
            
            # Atualizar labels
            if 'total' in self.stats_labels and self.stats_labels['total'].winfo_exists():
                self.stats_labels['total'].config(text=str(total))
            if 'success' in self.stats_labels and self.stats_labels['success'].winfo_exists():
                self.stats_labels['success'].config(text=str(success))
            if 'warning' in self.stats_labels and self.stats_labels['warning'].winfo_exists():
                self.stats_labels['warning'].config(text=str(warning))
            if 'error' in self.stats_labels and self.stats_labels['error'].winfo_exists():
                self.stats_labels['error'].config(text=str(error))
        except Exception as e:
            print(f"[ERROR] LogsScreen: Erro ao atualizar valores de stats: {e}")
    
    def _build_logs_table(self):
        table_card = Card(self.scrollable_frame, theme=self.theme)
        table_card.pack(fill='both', expand=True, padx=24, pady=(0, 16))
        table_card.add_padding(20)
        
        # Colunas da tabela
        columns = [
            {'title': '🕐 Data/Hora', 'width': 18},
            {'title': '📦 Job', 'width': 22},
            {'title': '📊 Status', 'type': 'badge', 'width': 12},
            {'title': '📝 Mensagem', 'flex': True},
            {'title': '🔢 Ocorrências', 'width': 12},
        ]
        
        self.table = ModernTable(
            table_card,
            columns=columns,
            theme=self.theme,
            on_row_click=self._show_log_details
        )
        self.table.pack(fill='both', expand=True)
        
        # Carregar logs da página atual
        self._load_page_logs()
    
    def _build_pagination(self):
        pagination_card = Card(self.scrollable_frame, theme=self.theme)
        pagination_card.pack(fill='x', padx=24, pady=(0, 24))
        pagination_card.add_padding(16)
        
        container = tk.Frame(pagination_card, bg=self.theme.BG_PRIMARY)
        container.pack()
        
        # Info de registros
        start = (self.current_page - 1) * self.logs_per_page + 1
        end = min(self.current_page * self.logs_per_page, len(self.filtered_logs))
        total = len(self.filtered_logs)
        
        self.info_label = tk.Label(
            container,
            text=f"Mostrando {start}-{end} de {total} logs",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        )
        self.info_label.pack(side='left', padx=(0, 32))
        
        # Paginação
        total_pages = max(1, (len(self.filtered_logs) + self.logs_per_page - 1) // self.logs_per_page)
        self.pagination = Pagination(
            container,
            total_pages=total_pages,
            current_page=self.current_page,
            on_page_change=self._on_page_change,
            theme=self.theme
        )
        self.pagination.pack(side='left')
    
    # ========== MÉTODOS DE DADOS ==========
    
    def _load_logs_from_api(self):
        """Carrega logs da API do OKING Hub"""
        try:
            # Verificar se temos token e shortname
            if not self.shortname or not self.token_manager:
                print("[WARN] LogsScreen: shortname ou token_manager não fornecidos, usando dados vazios")
                self.all_logs = []
                self.filtered_logs = []
                self._apply_filters()
                return
            
            # Obter token ativo
            active_token = self.token_manager.get_active_token()
            if not active_token:
                print("[WARN] LogsScreen: Nenhum token ativo")
                self.all_logs = []
                self.filtered_logs = []
                self._apply_filters()
                return
            
            token_value = active_token.get('token', '')
            
            # Construir parâmetros da query baseado nos filtros
            params = {'token': token_value}
            
            # Filtro de Job
            job_filter = self.filter_job.get()
            if job_filter and job_filter != "Todos":
                params['nome_job'] = job_filter
            
            # Filtro de Status (mapear para tipo da API)
            status_filter = self.filter_status.get()
            if status_filter and status_filter != "Todos":
                status_map = {
                    'Sucesso': 'X',
                    'Aviso': 'V',
                    'Erro': 'E',
                    'Info': 'I'
                }
                tipo = status_map.get(status_filter)
                if tipo:
                    params['tipo'] = tipo
            
            # Filtro de Data/Período
            date_filter = self.filter_date.get()
            if date_filter and date_filter != "Todos":
                from datetime import datetime, timedelta
                now = datetime.now()
                
                if date_filter == "Hoje":
                    params['data_inicio'] = now.strftime('%Y-%m-%d 00:00:00')
                elif date_filter == "Últimos 7 dias":
                    params['data_inicio'] = (now - timedelta(days=7)).strftime('%Y-%m-%d 00:00:00')
                elif date_filter == "Últimos 30 dias":
                    params['data_inicio'] = (now - timedelta(days=30)).strftime('%Y-%m-%d 00:00:00')
            
            # Filtro de Busca (mensagem)
            search_term = self.search_var.get().strip()
            if search_term:
                params['mensagem'] = search_term
            
            # Montar URL da API com parâmetros
            base_url = self.token_manager.get_base_url()
            query_string = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
            api_url = f"https://{base_url}/api/consulta/log/filtros?{query_string}"
            
            print(f"[INFO] LogsScreen: Carregando logs da API com filtros")
            print(f"[DEBUG] LogsScreen: Filtros aplicados: Job={job_filter}, Status={status_filter}, Data={date_filter}, Busca={search_term}")
            print(f"[DEBUG] LogsScreen: URL completa: {api_url}")
            print(f"[DEBUG] LogsScreen: Base URL: {base_url}")
            print(f"[DEBUG] LogsScreen: Token (primeiros 10 chars): {token_value[:10]}...")
            
            # Fazer requisição
            req = urllib.request.Request(api_url, headers={'Accept': 'application/json'})
            
            print(f"[DEBUG] LogsScreen: Fazendo requisição GET...")
            
            with urllib.request.urlopen(req, timeout=15) as response:
                print(f"[DEBUG] LogsScreen: Status HTTP: {response.status}")
                
                response_data = response.read().decode('utf-8')
                print(f"[DEBUG] LogsScreen: Tamanho da resposta: {len(response_data)} bytes")
                print(f"[DEBUG] LogsScreen: Primeiros 200 chars da resposta: {response_data[:200]}")
                
                # Verificar se a resposta é "Retorno sem dados!" ou similar
                if response_data.strip() in ["Retorno sem dados!", "Sem dados", "[]", ""]:
                    print("[INFO] LogsScreen: API retornou sem dados")
                    self.all_logs = []
                    self.filtered_logs = []
                    self._apply_filters()
                    
                    ToastNotification(
                        self.winfo_toplevel(), 
                        "Nenhum log encontrado para os filtros aplicados", 
                        duration=3000, 
                        theme=self.theme
                    )
                    return
                
                # Tentar fazer parse do JSON
                try:
                    data = json.loads(response_data)
                except json.JSONDecodeError as json_err:
                    print(f"[ERROR] LogsScreen: Resposta não é JSON válido: {response_data[:500]}")
                    print(f"[ERROR] LogsScreen: JSONDecodeError: {json_err}")
                    
                    # Se a API retornou texto não-JSON, tratar como sem dados
                    self.all_logs = []
                    self.filtered_logs = []
                    self._apply_filters()
                    
                    ToastNotification(
                        self.winfo_toplevel(), 
                        f"API retornou resposta inválida:\n{response_data[:100]}", 
                        duration=4000, 
                        theme=self.theme
                    )
                    return
                
                # Parse dos logs conforme estrutura da API
                if isinstance(data, dict):
                    print(f"[DEBUG] LogsScreen: Resposta é dict, chaves: {list(data.keys())}")
                    logs_raw = data.get('logs', data.get('data', data.get('registros', [])))
                else:
                    print(f"[DEBUG] LogsScreen: Resposta é {type(data).__name__}")
                    logs_raw = data
                
                print(f"[INFO] LogsScreen: {len(logs_raw) if isinstance(logs_raw, list) else 0} logs brutos encontrados")
                
                # Transformar para formato interno
                # JSON retorna: Tipo, Mensagem, nome_job, Ocorrências, identificador, Primeira Ocorrência, Última Ocorrências
                self.all_logs = []
                for i, log in enumerate(logs_raw):
                    if i < 3:  # Log dos 3 primeiros para debug
                        print(f"[DEBUG] LogsScreen: Log {i+1} keys: {list(log.keys()) if isinstance(log, dict) else 'not dict'}")
                    
                    # Mapear campos corretos do JSON
                    occurrences = log.get('Ocorrências', 0)
                    self.all_logs.append({
                        'id': log.get('identificador', ''),
                        'datetime': self._format_datetime(log.get('Última Ocorrências', log.get('Primeira Ocorrência', ''))),
                        'job': log.get('nome_job', 'Desconhecido'),
                        'status': self._normalize_status(log.get('Tipo', 'I')),
                        'message': log.get('Mensagem', ''),
                        'duration': f"{occurrences}x",  # Mostrar quantidade de ocorrências
                        'occurrences': occurrences,  # Número puro para uso em outras partes
                        'first_occurrence': log.get('Primeira Ocorrência', 'N/A'),
                        'last_occurrence': log.get('Última Ocorrências', 'N/A'),
                        'details': f"Identificador: {log.get('identificador', 'N/A')}\n"
                                  f"Ocorrências: {occurrences}\n"
                                  f"Primeira: {log.get('Primeira Ocorrência', 'N/A')}\n"
                                  f"Última: {log.get('Última Ocorrências', 'N/A')}\n"
                                  f"Mensagem: {log.get('Mensagem', '')}",
                        'raw': log  # Manter dados originais
                    })
                
                print(f"[INFO] LogsScreen: {len(self.all_logs)} logs carregados e formatados com sucesso!")
                
                if len(self.all_logs) > 0:
                    print(f"[DEBUG] LogsScreen: Exemplo do primeiro log formatado:")
                    print(f"  - datetime: {self.all_logs[0]['datetime']}")
                    print(f"  - job: {self.all_logs[0]['job']}")
                    print(f"  - status: {self.all_logs[0]['status']}")
                    print(f"  - message: {self.all_logs[0]['message'][:50]}...")
                
                self._apply_filters()
                
                # Mostrar toast com resultado da busca
                filtros_ativos = []
                if job_filter and job_filter != "Todos":
                    filtros_ativos.append(f"Job: {job_filter}")
                if status_filter and status_filter != "Todos":
                    filtros_ativos.append(f"Status: {status_filter}")
                if date_filter and date_filter != "Todos":
                    filtros_ativos.append(date_filter)
                if search_term:
                    filtros_ativos.append(f"Busca: {search_term}")
                
                # Construir mensagem do toast
                if filtros_ativos:
                    filtros_msg = " | ".join(filtros_ativos)
                    toast_msg = f"Encontrados {len(self.all_logs)} logs\n{filtros_msg}"
                else:
                    toast_msg = f"Encontrados {len(self.all_logs)} logs (todos)"
                
                ToastNotification(
                    self.winfo_toplevel(), 
                    toast_msg, 
                    duration=3000, 
                    theme=self.theme
                )
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else 'No error body'
            print(f"[ERROR] LogsScreen: Erro HTTP {e.code} ao carregar logs")
            print(f"[ERROR] LogsScreen: URL: {e.url}")
            print(f"[ERROR] LogsScreen: Headers: {e.headers}")
            print(f"[ERROR] LogsScreen: Body: {error_body[:500]}")
            
            if e.code == 404:
                print("[WARN] LogsScreen: Endpoint /api/consulta/log/filtros retornou 404")
                print("[INFO] LogsScreen: API pode estar sem logs ou endpoint indisponível")
                self.all_logs = []
                self.filtered_logs = []
                self._apply_filters()
            else:
                messagebox.showerror(
                    "Erro HTTP",
                    f"Erro ao carregar logs (HTTP {e.code}):\n{error_body[:200]}"
                )
        except urllib.error.URLError as e:
            print(f"[ERROR] LogsScreen: Erro de conexão com API: {e}")
            print(f"[ERROR] LogsScreen: Reason: {e.reason}")
            messagebox.showerror(
                "Erro de Conexão",
                f"Não foi possível conectar à API:\n{str(e.reason)}"
            )
        except Exception as e:
            print(f"[ERROR] LogsScreen: Erro ao carregar logs: {e}")
            import traceback
            print(f"[ERROR] LogsScreen: Traceback completo:")
            traceback.print_exc()
            messagebox.showerror(
                "Erro",
                f"Erro ao carregar logs:\n{str(e)}"
            )
    
    def _update_job_combo(self):
        """Atualiza o combo de jobs com os jobs configurados retornados da API"""
        try:
            if self.job_combo is None or not self.job_combo.winfo_exists():
                return
            
            # Verificar se temos token e shortname
            if not self.shortname or not self.token_manager:
                print("[WARN] LogsScreen: shortname ou token_manager não fornecidos para atualizar combo")
                return
            
            # Obter token ativo
            active_token = self.token_manager.get_active_token()
            if not active_token:
                print("[WARN] LogsScreen: Nenhum token ativo para atualizar combo")
                return
            
            token_value = active_token.get('token', '')
            
            # Buscar jobs configurados da mesma API usada na tela de Jobs
            base_url = self.token_manager.get_base_url()
            api_url = f"https://{base_url}/api/consulta/oking_hub/filtros?token={token_value}"
            
            print(f"[INFO] LogsScreen: Buscando jobs configurados da API...")
            
            req = urllib.request.Request(api_url, headers={'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                modulos = data.get('modulos', [])
                
                # Extrair nomes únicos dos jobs
                job_names = []
                for modulo in modulos:
                    job_name = modulo.get('job', modulo.get('job_name', ''))
                    if job_name:
                        job_names.append(job_name)
                
                # Ordenar e remover duplicatas
                unique_jobs = sorted(set(job_names))
                
                # Adicionar "Todos" no início
                job_values = ["Todos"] + unique_jobs
                
                # Atualizar combo
                self.job_combo['values'] = job_values
                
                print(f"[INFO] LogsScreen: Combo atualizado com {len(unique_jobs)} jobs da API")
                
        except Exception as e:
            print(f"[ERROR] LogsScreen: Erro ao atualizar combo de jobs: {e}")
            # Em caso de erro, usar dict_all_jobs como fallback
            try:
                job_list = [job_info.get('job_description', job_key) 
                           for job_key, job_info in dict_all_jobs.items()]
                job_list.sort()
                self.job_combo['values'] = ["Todos"] + job_list
                print(f"[INFO] LogsScreen: Combo atualizado com {len(job_list)} jobs do fallback")
            except:
                pass
    
    def _format_datetime(self, dt_string):
        """Formata string de data/hora para formato consistente"""
        if not dt_string:
            return datetime.now().strftime('%d/%m/%Y %H:%M')
        
        try:
            # Tentar vários formatos comuns
            formats = [
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y %H:%M',
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(dt_string.split('.')[0], fmt)
                    return dt.strftime('%d/%m/%Y %H:%M')
                except:
                    continue
            
            # Se não conseguiu parsear, retorna como está
            return dt_string
        except:
            return dt_string
    
    def _normalize_status(self, status):
        """Normaliza status para formato consistente"""
        # Tipos da API: X (Execução/Sucesso), I (Info), V (aViso), E (Erro)
        status_str = str(status).upper().strip()
        
        if status_str in ['X', 'SUCCESS', 'SUCESSO', 'OK', 'CONCLUIDO', 'COMPLETED']:
            return 'Sucesso'
        elif status_str in ['V', 'W', 'WARNING', 'AVISO', 'WARN', 'ALERTA']:
            return 'Aviso'
        elif status_str in ['E', 'ERROR', 'ERRO', 'FALHA', 'FAILED']:
            return 'Erro'
        elif status_str in ['I', 'INFO', 'INFORMATION']:
            return 'Info'
        else:
            return 'Info'
    
    def _apply_filters(self):
        """Aplica filtros aos logs"""
        self.filtered_logs = self.all_logs.copy()
        
        # Filtro por job
        if self.filter_job.get() != "Todos":
            self.filtered_logs = [log for log in self.filtered_logs if log['job'] == self.filter_job.get()]
        
        # Filtro por status
        if self.filter_status.get() != "Todos":
            self.filtered_logs = [log for log in self.filtered_logs if log['status'] == self.filter_status.get()]
        
        # Filtro por busca
        search = self.search_var.get().lower()
        if search:
            self.filtered_logs = [log for log in self.filtered_logs 
                                 if search in log['message'].lower() or search in log['job'].lower()]
        
        # Resetar para página 1
        self.current_page = 1
        
        # Atualizar tabela e paginação
        self._load_page_logs()
        self._update_pagination()
        self._update_stats()
    
    def _load_page_logs(self):
        """Carrega logs da página atual"""
        self.table.clear()
        
        start = (self.current_page - 1) * self.logs_per_page
        end = start + self.logs_per_page
        page_logs = self.filtered_logs[start:end]
        
        for log in page_logs:
            self.table.add_row(
                [log['datetime'], log['job'], log['status'], log['message'], log['duration']],
                row_data=log
            )
    
    def _update_pagination(self):
        """Atualiza controle de paginação"""
        total_pages = max(1, (len(self.filtered_logs) + self.logs_per_page - 1) // self.logs_per_page)
        self.pagination.update_pagination(total_pages, self.current_page)
        
        # Atualizar info
        start = (self.current_page - 1) * self.logs_per_page + 1
        end = min(self.current_page * self.logs_per_page, len(self.filtered_logs))
        total = len(self.filtered_logs)
        self.info_label.configure(text=f"Mostrando {start}-{end} de {total} logs")
    
    def _update_stats(self):
        """Atualiza estatísticas"""
        try:
            # Se stats_card existe, apenas atualizar valores
            if self.stats_card is not None and self.stats_card.winfo_exists():
                self._update_stats_values()
            else:
                # Recriar do zero se não existe
                self._build_stats()
        except Exception as e:
            print(f"[ERROR] LogsScreen: Erro ao atualizar stats: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_page_change(self, new_page):
        """Callback de mudança de página"""
        self.current_page = new_page
        self._load_page_logs()
        self._update_pagination()
    
    # ========== AÇÕES ==========
    
    def _toggle_auto_refresh(self):
        """Alterna auto-refresh de logs"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        
        if self.auto_refresh_enabled:
            self.auto_refresh_btn.config(text="🔄 Auto-refresh ON")
            self._schedule_refresh()
            print("[INFO] LogsScreen: Auto-refresh ativado")
        else:
            self.auto_refresh_btn.config(text="🔄 Auto-refresh OFF")
            if self.refresh_job:
                self.after_cancel(self.refresh_job)
                self.refresh_job = None
            print("[INFO] LogsScreen: Auto-refresh desativado")
    
    def _schedule_refresh(self):
        """Agenda próxima atualização automática"""
        if self.auto_refresh_enabled:
            try:
                # Verificar se a tela ainda existe
                if not self.winfo_exists():
                    self.auto_refresh_enabled = False
                    return
                
                print("[INFO] LogsScreen: Executando refresh automático...")
                
                # Contar logs antes do refresh
                old_count = len(self.all_logs)
                
                # Carregar logs
                self._load_logs_from_api()
                
                # Mostrar notificação toast
                new_count = len(self.all_logs)
                if new_count != old_count:
                    message = f"Logs atualizados: {new_count} registros ({new_count - old_count:+d})"
                else:
                    message = f"Logs atualizados: {new_count} registros"
                
                ToastNotification(self.winfo_toplevel(), message, duration=2000, theme=self.theme)
                
                # Agendar próximo refresh
                self.refresh_job = self.after(self.auto_refresh_interval, self._schedule_refresh)
            except Exception as e:
                print(f"[ERROR] LogsScreen: Erro no auto-refresh: {e}")
                self.auto_refresh_enabled = False
                if hasattr(self, 'auto_refresh_btn') and self.auto_refresh_btn.winfo_exists():
                    self.auto_refresh_btn.config(text="🔄 Auto-refresh OFF")
    
    def _show_log_details(self, log_data):
        """Mostra detalhes completos do log"""
        details = tk.Toplevel(self.winfo_toplevel())
        details.title(f"Detalhes do Log - {log_data['job']}")
        details.geometry("800x600")
        details.configure(bg=self.theme.BG_SECONDARY)
        
        # Modal
        details.transient(self.winfo_toplevel())
        details.grab_set()
        
        # Container scrollável
        canvas = tk.Canvas(details, bg=self.theme.BG_SECONDARY, highlightthickness=0)
        scrollbar = tk.Scrollbar(details, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.theme.BG_SECONDARY)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)
        
        # Configurar scroll com mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Vincular scroll também aos widgets filhos
        def _bind_child_mousewheel(widget):
            widget.bind('<Enter>', _bind_to_mousewheel)
            widget.bind('<Leave>', _unbind_from_mousewheel)
            for child in widget.winfo_children():
                _bind_child_mousewheel(child)
        
        _bind_child_mousewheel(scroll_frame)
        
        # Header
        header = Card(scroll_frame, theme=self.theme)
        header.pack(fill='x', pady=(0, 16))
        header.add_padding(20)
        
        tk.Label(
            header,
            text=f"📋 {log_data['job']}",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w')
        
        tk.Label(
            header,
            text=f"{log_data['datetime']} • Ocorrências: {log_data.get('occurrences', log_data.get('duration', '0'))}",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(4, 0))
        
        # Status
        status_map = {
            'sucesso': 'success',
            'aviso': 'warning',
            'erro': 'error'
        }
        StatusBadge(
            header,
            text=log_data['status'],
            status=status_map.get(log_data['status'].lower(), 'info'),
            theme=self.theme
        ).pack(anchor='w', pady=(8, 0))
        
        # Mensagem principal
        message_card = Card(scroll_frame, theme=self.theme)
        message_card.pack(fill='x', pady=(0, 16))
        message_card.add_padding(20)
        
        tk.Label(
            message_card,
            text="📝 Mensagem:",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x', pady=(0, 8))
        
        tk.Label(
            message_card,
            text=log_data['message'],
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_TERTIARY,
            anchor='w',
            justify='left',
            wraplength=720,
            padx=12,
            pady=12
        ).pack(fill='x')
        
        # Detalhes completos
        details_card = Card(scroll_frame, theme=self.theme)
        details_card.pack(fill='both', expand=True, pady=(0, 16))
        details_card.add_padding(20)
        
        tk.Label(
            details_card,
            text="🔍 Detalhes Completos:",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x', pady=(0, 8))
        
        details_text = tk.Text(
            details_card,
            height=15,
            font=self.theme.get_font("sm", mono=True),
            bg=self.theme.BG_CODE,
            fg=self.theme.TEXT_CODE,
            relief='flat',
            borderwidth=0,
            padx=12,
            pady=8,
            wrap='word'
        )
        details_text.pack(fill='both', expand=True)
        
        # Inserir detalhes formatados
        details_lines = []
        details_lines.append("="*60)
        details_lines.append("INFORMAÇÕES DO LOG")
        details_lines.append("="*60)
        details_lines.append("")
        details_lines.append(f"Job: {log_data['job']}")
        details_lines.append(f"Identificador: {log_data.get('id', 'N/A')}")
        details_lines.append(f"Status: {log_data['status']}")
        details_lines.append(f"Ocorrências: {log_data.get('occurrences', 0)}")
        details_lines.append("")
        details_lines.append(f"Primeira Ocorrência: {log_data.get('first_occurrence', 'N/A')}")
        details_lines.append(f"Última Ocorrência: {log_data.get('last_occurrence', 'N/A')}")
        details_lines.append("")
        details_lines.append("="*60)
        details_lines.append("MENSAGEM")
        details_lines.append("="*60)
        details_lines.append("")
        details_lines.append(log_data['message'])
        
        # Se tiver dados raw (JSON), formatar bonito
        if 'raw' in log_data and log_data['raw']:
            try:
                details_lines.append("")
                details_lines.append("")
                details_lines.append("="*60)
                details_lines.append("DADOS COMPLETOS (JSON)")
                details_lines.append("="*60)
                details_lines.append("")
                details_lines.append(json.dumps(log_data['raw'], indent=2, ensure_ascii=False))
            except Exception as e:
                details_lines.append(f"\n[Erro ao formatar JSON: {e}]")
        
        details_content = "\n".join(details_lines)
        details_text.insert('1.0', details_content)
        details_text.configure(state='disabled')
        
        # Botões
        buttons_frame = tk.Frame(scroll_frame, bg=self.theme.BG_SECONDARY)
        buttons_frame.pack(fill='x', pady=(0, 16))
        
        ModernButton(
            buttons_frame,
            text="📋 Copiar Detalhes",
            variant="secondary",
            theme=self.theme,
            command=lambda: self._copy_log_details(details_content, details)
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons_frame,
            text="Fechar",
            variant="primary",
            theme=self.theme,
            command=details.destroy
        ).pack(side='left')
        
        # Centralizar
        details.update_idletasks()
        x = (details.winfo_screenwidth() // 2) - (details.winfo_width() // 2)
        y = (details.winfo_screenheight() // 2) - (details.winfo_height() // 2)
        details.geometry(f"+{x}+{y}")
    
    def _copy_log_details(self, content, parent_window):
        """Copia detalhes do log para clipboard"""
        try:
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(content)
            messagebox.showinfo(
                "Copiado!",
                "Detalhes do log copiados para a área de transferência!",
                parent=parent_window
            )
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao copiar detalhes:\n{str(e)}",
                parent=parent_window
            )
    
    def _refresh_logs(self):
        """Atualiza logs manualmente"""
        print("[INFO] LogsScreen: Atualizando logs manualmente...")
        self._load_logs_from_api()
        
        # Mostrar toast em vez de messagebox
        ToastNotification(
            self.winfo_toplevel(), 
            f"Logs atualizados: {len(self.all_logs)} registros", 
            duration=2500, 
            theme=self.theme
        )
    
    def _export_logs(self):
        """Exporta logs filtrados para arquivo"""
        if not self.filtered_logs:
            messagebox.showwarning("Aviso", "Não há logs para exportar!")
            return
        
        # Escolher formato
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Arquivo CSV", "*.csv"),
                ("Arquivo de Texto", "*.txt"),
                ("Arquivo JSON", "*.json"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if not filename:
            return
        
        try:
            ext = Path(filename).suffix.lower()
            
            if ext == '.csv':
                # Exportar como CSV
                with open(filename, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Data/Hora', 'Job', 'Status', 'Mensagem', 'Ocorrências'])
                    for log in self.filtered_logs:
                        writer.writerow([
                            log['datetime'],
                            log['job'],
                            log['status'],
                            log['message'],
                            log['duration']
                        ])
            
            elif ext == '.json':
                # Exportar como JSON
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.filtered_logs, f, indent=2, ensure_ascii=False)
            
            else:
                # Exportar como TXT
                with open(filename, 'w', encoding='utf-8') as f:
                    for log in self.filtered_logs:
                        f.write(f"{log['datetime']} | {log['job']} | {log['status']} | {log['message']}\n")
                        f.write(f"  Ocorrências: {log['duration']}\n")
                        if log.get('details'):
                            f.write(f"  Detalhes: {log['details'][:200]}...\n")
                        f.write("\n")
            
            messagebox.showinfo(
                "Sucesso!",
                f"{len(self.filtered_logs)} logs exportados para:\n{filename}"
            )
            print(f"[INFO] LogsScreen: {len(self.filtered_logs)} logs exportados para {filename}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar logs:\n{str(e)}")
            print(f"[ERROR] LogsScreen: Erro ao exportar logs: {e}")
    
    def _clear_logs(self):
        """Limpa todos os logs (API)"""
        if not messagebox.askyesno(
            "Limpar Logs",
            "Deseja realmente limpar TODOS os logs do sistema?\n\n"
            "⚠️ Esta ação não pode ser desfeita!\n"
            "⚠️ Os logs serão removidos permanentemente do servidor."
        ):
            return
        
        try:
            # Verificar se temos token e shortname
            if not self.shortname or not self.token_manager:
                messagebox.showerror("Erro", "Não é possível limpar logs: shortname ou token não disponíveis")
                return
            
            # Obter token ativo
            active_token = self.token_manager.get_active_token()
            if not active_token:
                messagebox.showerror("Erro", "Nenhum token ativo encontrado")
                return
            
            token_value = active_token.get('token', '')
            
            # Montar URL da API (endpoint para limpar logs)
            base_url = self.token_manager.get_base_url()
            api_url = f"https://{base_url}/api/logs/limpar"
            
            dados = {'token': token_value}
            
            req = urllib.request.Request(
                api_url,
                data=json.dumps(dados).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            print(f"[INFO] LogsScreen: Limpando logs via API...")
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('sucesso'):
                    self.all_logs = []
                    self.filtered_logs = []
                    self.current_page = 1
                    self._load_page_logs()
                    self._update_pagination()
                    self._update_stats()
                    
                    messagebox.showinfo("Sucesso!", "Todos os logs foram removidos com sucesso!")
                    print("[INFO] LogsScreen: Logs limpos com sucesso")
                else:
                    raise Exception(result.get('mensagem', 'Erro desconhecido'))
                    
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Endpoint não existe, limpar apenas localmente
                self.all_logs = []
                self.filtered_logs = []
                self.current_page = 1
                self._load_page_logs()
                self._update_pagination()
                self._update_stats()
                messagebox.showinfo("Aviso", "Logs limpos localmente (endpoint de limpeza não disponível)")
            else:
                messagebox.showerror("Erro HTTP", f"Erro ao limpar logs (HTTP {e.code}):\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao limpar logs:\n{str(e)}")
            print(f"[ERROR] LogsScreen: Erro ao limpar logs: {e}")
