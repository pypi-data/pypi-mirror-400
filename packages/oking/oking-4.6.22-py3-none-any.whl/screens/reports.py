"""
📊 Tela de Relatórios - OKING Hub
Interface moderna em Tkinter para visualizar relatórios de execução
Com filtros, busca e exportação
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime, timedelta
import random

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from ui_components import ModernTheme, Card, ModernButton, StatusBadge


# ==================== COMPONENTES ====================

class ReportCard(tk.Frame):
    """Card de relatório individual"""
    def __init__(self, parent, report_data, theme=None, on_view=None, on_export=None):
        self.theme = theme or ModernTheme()
        super().__init__(
            parent,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.BORDER
        )
        
        self.report_data = report_data
        self.on_view = on_view
        self.on_export = on_export
        
        self._build_card()
    
    def _build_card(self):
        container = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=16, pady=12)
        
        # Header
        header = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        header.pack(fill='x', pady=(0, 8))
        
        # Esquerda: Job e status
        left = tk.Frame(header, bg=self.theme.BG_PRIMARY)
        left.pack(side='left')
        
        tk.Label(
            left,
            text=f"📋 {self.report_data['job_name']}",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 12))
        
        status = self.report_data.get('status', 'info')
        status_text = {
            'success': '✓ Sucesso',
            'warning': '⚠ Alerta',
            'error': '✗ Erro',
            'info': 'ℹ Info'
        }.get(status, 'Info')
        
        StatusBadge(left, text=status_text, status=status, theme=self.theme).pack(side='left')
        
        # Direita: Ações
        right = tk.Frame(header, bg=self.theme.BG_PRIMARY)
        right.pack(side='right')
        
        ModernButton(
            right,
            text="👁️",
            variant="secondary",
            theme=self.theme,
            command=lambda: self.on_view and self.on_view(self.report_data),
            width=2,
            padx=8,
            pady=6
        ).pack(side='left', padx=(0, 4))
        
        ModernButton(
            right,
            text="📥",
            variant="primary",
            theme=self.theme,
            command=lambda: self.on_export and self.on_export(self.report_data),
            width=2,
            padx=8,
            pady=6
        ).pack(side='left')
        
        # Informações
        info = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        info.pack(fill='x')
        
        # Data e hora
        executed_at = self.report_data.get('executed_at', '')
        if executed_at:
            try:
                dt = datetime.fromisoformat(executed_at)
                date_display = dt.strftime('%d/%m/%Y %H:%M:%S')
            except:
                date_display = executed_at
        else:
            date_display = 'N/A'
        
        tk.Label(
            info,
            text=f"📅 {date_display}",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x', pady=(0, 4))
        
        # Duração
        duration = self.report_data.get('duration', 0)
        duration_display = f"{duration}s" if duration < 60 else f"{duration//60}min {duration%60}s"
        
        tk.Label(
            info,
            text=f"⏱️ Duração: {duration_display}",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x', pady=(0, 4))
        
        # Registros processados
        records = self.report_data.get('records_processed', 0)
        
        tk.Label(
            info,
            text=f"📊 Registros processados: {records:,}",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x')


class ReportDetailDialog(tk.Toplevel):
    """Dialog para visualizar detalhes do relatório"""
    def __init__(self, parent, report_data, theme=None):
        super().__init__(parent)
        self.theme = theme or ModernTheme()
        self.report_data = report_data
        
        self.title("Detalhes do Relatório")
        self.geometry("700x600")
        self.configure(bg=self.theme.BG_SECONDARY)
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        self._build_dialog()
        
        # Centraliza
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _build_dialog(self):
        main = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        main.pack(fill='both', expand=True, padx=24, pady=24)
        
        # Título
        tk.Label(
            main,
            text=f"📋 {self.report_data['job_name']}",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY
        ).pack(anchor='w', pady=(0, 20))
        
        # Card com informações
        card = Card(main, theme=self.theme)
        card.pack(fill='both', expand=True)
        card.add_padding(20)
        
        # Status
        status_frame = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        status_frame.pack(fill='x', pady=(0, 16))
        
        tk.Label(
            status_frame,
            text="Status:",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 8))
        
        status = self.report_data.get('status', 'info')
        status_text = {
            'success': '✓ Sucesso',
            'warning': '⚠ Alerta',
            'error': '✗ Erro',
            'info': 'ℹ Info'
        }.get(status, 'Info')
        
        StatusBadge(status_frame, text=status_text, status=status, theme=self.theme).pack(side='left')
        
        # Informações detalhadas
        info_text = tk.Text(
            card,
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_TERTIARY,
            relief='flat',
            borderwidth=0,
            wrap='word',
            height=20
        )
        info_text.pack(fill='both', expand=True, pady=(0, 16))
        
        # Popula informações
        executed_at = self.report_data.get('executed_at', '')
        if executed_at:
            try:
                dt = datetime.fromisoformat(executed_at)
                date_display = dt.strftime('%d/%m/%Y %H:%M:%S')
            except:
                date_display = executed_at
        else:
            date_display = 'N/A'
        
        duration = self.report_data.get('duration', 0)
        duration_display = f"{duration}s" if duration < 60 else f"{duration//60}min {duration%60}s"
        
        details = f"""📅 Data de Execução:
{date_display}

⏱️ Duração:
{duration_display}

📊 Registros Processados:
{self.report_data.get('records_processed', 0):,}

✓ Registros com Sucesso:
{self.report_data.get('records_success', 0):,}

✗ Registros com Erro:
{self.report_data.get('records_error', 0):,}

📝 Mensagem:
{self.report_data.get('message', 'Nenhuma mensagem disponível')}

🔍 Detalhes Técnicos:
{self.report_data.get('details', 'Nenhum detalhe técnico disponível')}
"""
        
        info_text.insert('1.0', details)
        info_text.configure(state='disabled')
        
        # Botão fechar
        ModernButton(
            main,
            text="Fechar",
            variant="secondary",
            theme=self.theme,
            command=self.destroy,
            width=12
        ).pack(pady=(16, 0))


# ==================== TELA PRINCIPAL ====================

class ReportsScreen(tk.Frame):
    """Tela de relatórios"""
    
    def __init__(self, parent):
        self.theme = ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY)
        
        # Dados
        self.reports = []
        self.filtered_reports = []
        
        # Filtros
        self.filter_status = tk.StringVar(value="Todos")
        self.filter_job = tk.StringVar(value="Todos")
        self.filter_period = tk.StringVar(value="Últimos 7 dias")
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._apply_filters())
        
        self._build_ui()
        self._load_sample_data()
    
    def _build_ui(self):
        # Canvas com scroll
        canvas = tk.Canvas(self, bg=self.theme.BG_SECONDARY, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme.BG_SECONDARY)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.scrollable_frame = scrollable_frame
        
        # Conteúdo
        self._build_header()
        self._build_stats()
        self._build_filters()
        self._build_reports_list()
    
    def _build_header(self):
        """Cabeçalho principal"""
        header = Card(self.scrollable_frame, theme=self.theme)
        header.pack(fill='x', padx=24, pady=24)
        header.add_padding(20)
        
        container = tk.Frame(header, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x')
        
        # Título
        tk.Label(
            container,
            text="📊 Relatórios",
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        # Direita: Ação
        ModernButton(
            container,
            text="📥 Exportar Todos",
            variant="success",
            theme=self.theme,
            command=self._export_all
        ).pack(side='right')
    
    def _build_stats(self):
        """Estatísticas"""
        stats_card = Card(self.scrollable_frame, theme=self.theme)
        stats_card.pack(fill='x', padx=24, pady=(0, 16))
        stats_card.add_padding(20)
        
        container = tk.Frame(stats_card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x')
        
        # Total
        self._create_stat_box(
            container,
            "📊 Total",
            str(len(self.reports)),
            self.theme.INFO
        ).pack(side='left', padx=(0, 16))
        
        # Sucesso
        success = len([r for r in self.reports if r.get('status') == 'success'])
        self._create_stat_box(
            container,
            "✓ Sucesso",
            str(success),
            self.theme.SUCCESS
        ).pack(side='left', padx=(0, 16))
        
        # Alertas
        warnings = len([r for r in self.reports if r.get('status') == 'warning'])
        self._create_stat_box(
            container,
            "⚠ Alertas",
            str(warnings),
            self.theme.WARNING
        ).pack(side='left', padx=(0, 16))
        
        # Erros
        errors = len([r for r in self.reports if r.get('status') == 'error'])
        self._create_stat_box(
            container,
            "✗ Erros",
            str(errors),
            self.theme.DANGER
        ).pack(side='left')
    
    def _create_stat_box(self, parent, label, value, color):
        box = tk.Frame(parent, bg=self.theme.BG_PRIMARY)
        
        tk.Label(
            box,
            text=label,
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack()
        
        tk.Label(
            box,
            text=value,
            font=self.theme.get_font("xxl", "bold"),
            fg=color,
            bg=self.theme.BG_PRIMARY
        ).pack()
        
        return box
    
    def _build_filters(self):
        """Filtros"""
        filters_card = Card(self.scrollable_frame, theme=self.theme)
        filters_card.pack(fill='x', padx=24, pady=(0, 16))
        filters_card.add_padding(20)
        
        # Título
        tk.Label(
            filters_card,
            text="🔍 Filtros",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 16))
        
        # Container de filtros
        filters = tk.Frame(filters_card, bg=self.theme.BG_PRIMARY)
        filters.pack(fill='x')
        
        # Busca
        search_frame = tk.Frame(filters, bg=self.theme.BG_PRIMARY)
        search_frame.pack(side='left', fill='x', expand=True, padx=(0, 16))
        
        tk.Label(
            search_frame,
            text="Buscar:",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 8))
        
        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_TERTIARY,
            relief='flat',
            borderwidth=0,
            width=30
        ).pack(side='left', ipady=6)
        
        # Status
        status_frame = tk.Frame(filters, bg=self.theme.BG_PRIMARY)
        status_frame.pack(side='left', padx=(0, 16))
        
        tk.Label(
            status_frame,
            text="Status:",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 8))
        
        ttk.Combobox(
            status_frame,
            textvariable=self.filter_status,
            values=['Todos', 'Sucesso', 'Alerta', 'Erro'],
            state='readonly',
            width=12
        ).pack(side='left')
        self.filter_status.trace('w', lambda *args: self._apply_filters())
        
        # Job
        job_frame = tk.Frame(filters, bg=self.theme.BG_PRIMARY)
        job_frame.pack(side='left', padx=(0, 16))
        
        tk.Label(
            job_frame,
            text="Job:",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 8))
        
        ttk.Combobox(
            job_frame,
            textvariable=self.filter_job,
            values=['Todos', 'Sincronizar Produtos', 'Atualizar Preços', 'Importar Pedidos', 'Enviar Estoque'],
            state='readonly',
            width=18
        ).pack(side='left')
        self.filter_job.trace('w', lambda *args: self._apply_filters())
        
        # Período
        period_frame = tk.Frame(filters, bg=self.theme.BG_PRIMARY)
        period_frame.pack(side='left')
        
        tk.Label(
            period_frame,
            text="Período:",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 8))
        
        ttk.Combobox(
            period_frame,
            textvariable=self.filter_period,
            values=['Hoje', 'Últimos 7 dias', 'Últimos 30 dias', 'Todos'],
            state='readonly',
            width=15
        ).pack(side='left')
        self.filter_period.trace('w', lambda *args: self._apply_filters())
    
    def _build_reports_list(self):
        """Lista de relatórios"""
        list_card = Card(self.scrollable_frame, theme=self.theme)
        list_card.pack(fill='both', expand=True, padx=24, pady=(0, 24))
        list_card.add_padding(20)
        
        # Título com contador
        header = tk.Frame(list_card, bg=self.theme.BG_PRIMARY)
        header.pack(fill='x', pady=(0, 16))
        
        tk.Label(
            header,
            text="📋 Relatórios",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        self.counter_label = tk.Label(
            header,
            text=f"({len(self.filtered_reports)} relatórios)",
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        )
        self.counter_label.pack(side='left', padx=(8, 0))
        
        # Container de relatórios
        self.reports_container = tk.Frame(list_card, bg=self.theme.BG_PRIMARY)
        self.reports_container.pack(fill='both', expand=True)
        
        self._render_reports()
    
    def _render_reports(self):
        """Renderiza lista de relatórios"""
        # Limpa
        for widget in self.reports_container.winfo_children():
            widget.destroy()
        
        # Atualiza contador
        if hasattr(self, 'counter_label'):
            self.counter_label.configure(text=f"({len(self.filtered_reports)} relatórios)")
        
        if not self.filtered_reports:
            # Mensagem vazia
            tk.Label(
                self.reports_container,
                text="📭 Nenhum relatório encontrado",
                font=self.theme.get_font("lg"),
                fg=self.theme.TEXT_TERTIARY,
                bg=self.theme.BG_PRIMARY
            ).pack(pady=40)
        else:
            # Renderiza relatórios
            for report_data in self.filtered_reports:
                ReportCard(
                    self.reports_container,
                    report_data=report_data,
                    theme=self.theme,
                    on_view=self._view_report,
                    on_export=self._export_report
                ).pack(fill='x', pady=(0, 12))
    
    # ========== MÉTODOS DE AÇÃO ==========
    
    def _apply_filters(self):
        """Aplica filtros"""
        self.filtered_reports = self.reports.copy()
        
        # Filtro de busca
        search = self.search_var.get().lower()
        if search:
            self.filtered_reports = [
                r for r in self.filtered_reports
                if search in r['job_name'].lower() or search in r.get('message', '').lower()
            ]
        
        # Filtro de status
        status_filter = self.filter_status.get()
        if status_filter != 'Todos':
            status_map = {
                'Sucesso': 'success',
                'Alerta': 'warning',
                'Erro': 'error'
            }
            self.filtered_reports = [
                r for r in self.filtered_reports
                if r.get('status') == status_map.get(status_filter)
            ]
        
        # Filtro de job
        job_filter = self.filter_job.get()
        if job_filter != 'Todos':
            self.filtered_reports = [
                r for r in self.filtered_reports
                if r['job_name'] == job_filter
            ]
        
        # Filtro de período
        period_filter = self.filter_period.get()
        if period_filter != 'Todos':
            now = datetime.now()
            if period_filter == 'Hoje':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period_filter == 'Últimos 7 dias':
                start_date = now - timedelta(days=7)
            elif period_filter == 'Últimos 30 dias':
                start_date = now - timedelta(days=30)
            
            self.filtered_reports = [
                r for r in self.filtered_reports
                if datetime.fromisoformat(r['executed_at']) >= start_date
            ]
        
        self._render_reports()
        self._update_stats()
    
    def _view_report(self, report_data):
        """Visualiza detalhes do relatório"""
        ReportDetailDialog(self.winfo_toplevel(), report_data, theme=self.theme)
    
    def _export_report(self, report_data):
        """Exporta relatório individual"""
        file_path = filedialog.asksaveasfilename(
            title="Exportar Relatório",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Texto", "*.txt"), ("Todos", "*.*")],
            initialfile=f"relatorio_{report_data['job_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Sucesso", f"Relatório exportado para:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar relatório:\n{str(e)}")
    
    def _export_all(self):
        """Exporta todos os relatórios filtrados"""
        if not self.filtered_reports:
            messagebox.showwarning("Aviso", "Nenhum relatório para exportar.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Todos os Relatórios",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
            initialfile=f"relatorios_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.filtered_reports, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo(
                    "Sucesso",
                    f"{len(self.filtered_reports)} relatório(s) exportado(s) para:\n{file_path}"
                )
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar relatórios:\n{str(e)}")
    
    def _update_stats(self):
        """Atualiza estatísticas"""
        # Reconstrói painel de stats
        children = self.scrollable_frame.winfo_children()
        if len(children) >= 2:
            children[1].destroy()
        
        # Recria stats
        stats_card = Card(self.scrollable_frame, theme=self.theme)
        stats_card.pack(fill='x', padx=24, pady=(0, 16), after=children[0])
        stats_card.add_padding(20)
        
        container = tk.Frame(stats_card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x')
        
        # Total
        self._create_stat_box(
            container,
            "📊 Total",
            str(len(self.filtered_reports)),
            self.theme.INFO
        ).pack(side='left', padx=(0, 16))
        
        # Sucesso
        success = len([r for r in self.filtered_reports if r.get('status') == 'success'])
        self._create_stat_box(
            container,
            "✓ Sucesso",
            str(success),
            self.theme.SUCCESS
        ).pack(side='left', padx=(0, 16))
        
        # Alertas
        warnings = len([r for r in self.filtered_reports if r.get('status') == 'warning'])
        self._create_stat_box(
            container,
            "⚠ Alertas",
            str(warnings),
            self.theme.WARNING
        ).pack(side='left', padx=(0, 16))
        
        # Erros
        errors = len([r for r in self.filtered_reports if r.get('status') == 'error'])
        self._create_stat_box(
            container,
            "✗ Erros",
            str(errors),
            self.theme.DANGER
        ).pack(side='left')
    
    def _load_sample_data(self):
        """Carrega dados de exemplo"""
        jobs = ['Sincronizar Produtos', 'Atualizar Preços', 'Importar Pedidos', 'Enviar Estoque']
        statuses = ['success', 'warning', 'error']
        
        # Gera 20 relatórios de exemplo
        for i in range(20):
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            
            executed_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            status = random.choice(statuses)
            job = random.choice(jobs)
            
            records = random.randint(100, 10000)
            records_error = random.randint(0, records // 10) if status != 'success' else 0
            
            self.reports.append({
                'id': i + 1,
                'job_name': job,
                'status': status,
                'executed_at': executed_at.isoformat(),
                'duration': random.randint(10, 300),
                'records_processed': records,
                'records_success': records - records_error,
                'records_error': records_error,
                'message': 'Execução concluída com sucesso' if status == 'success' else 
                          'Alguns registros falharam' if status == 'warning' else
                          'Falha na execução',
                'details': f'Log técnico do job {job}'
            })
        
        # Ordena por data (mais recente primeiro)
        self.reports.sort(key=lambda x: x['executed_at'], reverse=True)
        
        self.filtered_reports = self.reports.copy()
        self._render_reports()
