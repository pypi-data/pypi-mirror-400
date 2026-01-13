"""
Componentes reutilizáveis para a interface moderna
"""
import tkinter as tk
from tkinter import ttk
try:
    from src.ui.theme import ModernTheme
except ImportError:
    # Fallback para testes standalone
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.ui.theme import ModernTheme


class Card(tk.Frame):
    """Card moderno com sombra e bordas arredondadas"""
    
    def __init__(self, parent, theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        
        # Configurações padrão
        config = {
            'bg': self.theme.BG_PRIMARY,
            'relief': 'flat',
            'borderwidth': 1,
            'highlightthickness': 1,
            'highlightbackground': self.theme.BORDER,
            'highlightcolor': self.theme.BORDER,
        }
        config.update(kwargs)
        
        super().__init__(parent, **config)
        
    def add_padding(self, padding=None):
        """Adiciona padding interno ao card"""
        p = padding or self.theme.SPACING_MD
        self.configure(padx=p, pady=p)


class StatusBadge(tk.Label):
    """Badge de status colorido"""
    
    def __init__(self, parent, text="", status="info", theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        
        # Mapear status para cores
        status_colors = {
            'success': (self.theme.SUCCESS, self.theme.SUCCESS_BG),
            'warning': (self.theme.WARNING, self.theme.WARNING_BG),
            'danger': (self.theme.DANGER, self.theme.DANGER_BG),
            'info': (self.theme.INFO, self.theme.INFO_BG),
        }
        
        fg, bg = status_colors.get(status, (self.theme.TEXT_PRIMARY, self.theme.BG_TERTIARY))
        
        config = {
            'text': text,
            'font': self.theme.get_font("sm", "bold"),
            'fg': fg,
            'bg': bg,
            'padx': 12,
            'pady': 6,
            'relief': 'flat',
        }
        config.update(kwargs)
        
        super().__init__(parent, **config)


class ModernButton(tk.Button):
    """Botão moderno com hover effect"""
    
    def __init__(self, parent, text="", variant="primary", theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        self.variant = variant
        
        # Variantes de botão
        variants = {
            'primary': {
                'bg': self.theme.PRIMARY,
                'fg': 'white',
                'activebackground': self.theme.PRIMARY_DARK,
                'activeforeground': 'white',
            },
            'secondary': {
                'bg': self.theme.BG_TERTIARY,
                'fg': self.theme.TEXT_PRIMARY,
                'activebackground': self.theme.BORDER,
                'activeforeground': self.theme.TEXT_PRIMARY,
            },
            'success': {
                'bg': self.theme.SUCCESS,
                'fg': 'white',
                'activebackground': '#059669',
                'activeforeground': 'white',
            },
            'danger': {
                'bg': self.theme.DANGER,
                'fg': 'white',
                'activebackground': '#dc2626',
                'activeforeground': 'white',
            },
        }
        
        variant_config = variants.get(variant, variants['primary'])
        
        config = {
            'text': text,
            'font': self.theme.get_font("md", "bold"),
            'relief': 'flat',
            'borderwidth': 0,
            'padx': 20,
            'pady': 10,
            'cursor': 'hand2',
        }
        config.update(variant_config)
        config.update(kwargs)
        
        super().__init__(parent, **config)
        
        # Hover effect
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        
        self.default_bg = config.get('bg')
        self.hover_bg = config.get('activebackground')
        
    def _on_enter(self, event):
        self.configure(bg=self.hover_bg)
        
    def _on_leave(self, event):
        self.configure(bg=self.default_bg)


class MetricCard(Card):
    """Card para exibir métricas/estatísticas"""
    
    def __init__(self, parent, title="", value="", icon=None, status="info", theme=None):
        super().__init__(parent, theme=theme)
        self.theme = theme or ModernTheme()
        self.add_padding(self.theme.SPACING_LG)
        
        # Container interno
        container = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True)
        
        # Título
        title_label = tk.Label(
            container,
            text=title,
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        )
        title_label.pack(fill='x', pady=(0, self.theme.SPACING_SM))
        
        # Valor (métrica principal)
        self.value_label = tk.Label(
            container,
            text=value,
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        )
        self.value_label.pack(fill='x')
        
        # Badge de status (opcional)
        if status:
            status_colors = {
                'success': self.theme.SUCCESS,
                'warning': self.theme.WARNING,
                'danger': self.theme.DANGER,
                'info': self.theme.INFO,
            }
            color = status_colors.get(status, self.theme.TEXT_TERTIARY)
            
            indicator = tk.Frame(
                container,
                bg=color,
                height=4,
                width=40
            )
            indicator.pack(anchor='w', pady=(self.theme.SPACING_SM, 0))
    
    def update_value(self, new_value):
        """Atualiza o valor da métrica"""
        self.value_label.configure(text=new_value)


class JobCard(Card):
    """Card para exibir informações de um job"""
    
    def __init__(self, parent, job_name="", job_status="", last_run="", interval="", theme=None, on_edit=None, on_log=None):
        super().__init__(parent, theme=theme)
        self.theme = theme or ModernTheme()
        self.add_padding(self.theme.SPACING_MD)
        
        # Container principal
        main_container = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        main_container.pack(fill='both', expand=True)
        
        # Linha 1: Nome do job + Status
        top_row = tk.Frame(main_container, bg=self.theme.BG_PRIMARY)
        top_row.pack(fill='x', pady=(0, self.theme.SPACING_SM))
        
        # Nome do job
        name_label = tk.Label(
            top_row,
            text=job_name,
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        )
        name_label.pack(side='left')
        
        # Status badge
        status_map = {
            'ativo': ('✓ Ativo', 'success'),
            'inativo': ('○ Inativo', 'danger'),
            'executando': ('⟳ Executando', 'warning'),
        }
        status_text, status_type = status_map.get(job_status.lower(), (job_status, 'info'))
        
        status_badge = StatusBadge(
            top_row,
            text=status_text,
            status=status_type,
            theme=self.theme
        )
        status_badge.pack(side='right')
        
        # Linha 2: Informações de tempo
        info_row = tk.Frame(main_container, bg=self.theme.BG_PRIMARY)
        info_row.pack(fill='x', pady=(0, self.theme.SPACING_SM))
        
        # Última execução
        time_info = f"⏱ {interval} | 🕐 Última: {last_run}"
        time_label = tk.Label(
            info_row,
            text=time_info,
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        )
        time_label.pack(side='left')
        
        # Linha 3: Botões de ação
        actions_row = tk.Frame(main_container, bg=self.theme.BG_PRIMARY)
        actions_row.pack(fill='x')
        
        # Botão Editar
        if on_edit:
            edit_btn = tk.Button(
                actions_row,
                text="✏ Editar",
                font=self.theme.get_font("sm"),
                fg=self.theme.PRIMARY,
                bg=self.theme.BG_PRIMARY,
                relief='flat',
                cursor='hand2',
                borderwidth=0,
                command=on_edit
            )
            edit_btn.pack(side='left', padx=(0, self.theme.SPACING_MD))
        
        # Botão Logs
        if on_log:
            log_btn = tk.Button(
                actions_row,
                text="📋 Logs",
                font=self.theme.get_font("sm"),
                fg=self.theme.PRIMARY,
                bg=self.theme.BG_PRIMARY,
                relief='flat',
                cursor='hand2',
                borderwidth=0,
                command=on_log
            )
            log_btn.pack(side='left')
