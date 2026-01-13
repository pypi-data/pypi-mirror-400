"""
🎨 Componentes UI Reutilizáveis - OKING Hub
Componentes modernos em Tkinter compartilhados entre todas as telas
"""
import tkinter as tk
from tkinter import ttk


# ==================== TEMA ====================

class ModernTheme:
    """Tema moderno centralizado"""
    PRIMARY = "#2563eb"
    PRIMARY_DARK = "#1e40af"
    PRIMARY_LIGHT = "#3b82f6"
    BG_PRIMARY = "#ffffff"
    BG_SECONDARY = "#f8fafc"
    BG_TERTIARY = "#f1f5f9"
    BG_HOVER = "#f0f9ff"
    BG_CODE = "#1e293b"  # Fundo do editor de código
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#64748b"
    TEXT_TERTIARY = "#94a3b8"
    TEXT_CODE = "#e2e8f0"  # Texto do editor de código
    SUCCESS = "#10b981"
    SUCCESS_BG = "#d1fae5"
    WARNING = "#f59e0b"
    WARNING_BG = "#fef3c7"
    DANGER = "#ef4444"
    DANGER_BG = "#fee2e2"
    INFO = "#3b82f6"
    INFO_BG = "#dbeafe"
    BORDER = "#e2e8f0"
    FONT_FAMILY = "Segoe UI"
    FONT_CODE = "Consolas"  # Fonte monospace para código
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    
    def __init__(self, mode="light", base_font_size=12, compact_mode=False):
        """Inicializa tema com modo light/dark"""
        self.mode = mode
        self.base_font_size = base_font_size  # Tamanho base configurável
        self.compact_mode = compact_mode  # Modo compacto
        self.apply_mode(mode)
        self.apply_spacing()
    
    def apply_mode(self, mode):
        """Aplica modo light ou dark"""
        self.mode = mode
        
        if mode == "dark":
            # Dark mode colors
            self.BG_PRIMARY = "#1e293b"
            self.BG_SECONDARY = "#0f172a"
            self.BG_TERTIARY = "#334155"
            self.BG_HOVER = "#334155"
            self.BG_CODE = "#0f172a"
            self.TEXT_PRIMARY = "#f1f5f9"
            self.TEXT_SECONDARY = "#94a3b8"
            self.TEXT_TERTIARY = "#64748b"
            self.TEXT_CODE = "#e2e8f0"
            self.BORDER = "#334155"
            self.SUCCESS_BG = "#064e3b"
            self.WARNING_BG = "#78350f"
            self.DANGER_BG = "#7f1d1d"
            self.INFO_BG = "#1e3a8a"
        else:
            # Light mode colors (default)
            self.BG_PRIMARY = "#ffffff"
            self.BG_SECONDARY = "#f8fafc"
            self.BG_TERTIARY = "#f1f5f9"
            self.BG_HOVER = "#f0f9ff"
            self.BG_CODE = "#1e293b"
            self.TEXT_PRIMARY = "#0f172a"
            self.TEXT_SECONDARY = "#64748b"
            self.TEXT_TERTIARY = "#94a3b8"
            self.TEXT_CODE = "#e2e8f0"
            self.BORDER = "#e2e8f0"
            self.SUCCESS_BG = "#d1fae5"
            self.WARNING_BG = "#fef3c7"
            self.DANGER_BG = "#fee2e2"
            self.INFO_BG = "#dbeafe"
    
    def apply_spacing(self):
        """Aplica espaçamentos baseado no modo compacto"""
        if self.compact_mode:
            # Modo compacto - reduz espaçamentos em 50%
            self.SPACING_SM = 4
            self.SPACING_MD = 8
            self.SPACING_LG = 12
        else:
            # Modo normal
            self.SPACING_SM = 8
            self.SPACING_MD = 16
            self.SPACING_LG = 24
    
    def get_font(self, size="md", weight="normal", mono=False):
        """Retorna fonte configurada com escala baseada no tamanho configurado"""
        # Tamanhos relativos ao base_font_size (padrão 12)
        scale = self.base_font_size / 12.0
        base_sizes = {"xs": 8, "sm": 10, "md": 12, "lg": 16, "xl": 22, "xxl": 30}
        
        # Aplica escala
        font_size = int(base_sizes.get(size, 12) * scale)
        family = self.FONT_CODE if mono else self.FONT_FAMILY
        return (family, font_size, weight)


# ==================== COMPONENTES ====================

class Card(tk.Frame):
    """Card moderno com borda e sombra"""
    def __init__(self, parent, theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        config = {
            'bg': self.theme.BG_PRIMARY,
            'relief': 'flat',
            'borderwidth': 1,
            'highlightthickness': 1,
            'highlightbackground': self.theme.BORDER,
        }
        config.update(kwargs)
        super().__init__(parent, **config)
    
    def add_padding(self, padding=None):
        """Adiciona padding interno"""
        p = padding or self.theme.SPACING_MD
        self.configure(padx=p, pady=p)


class ModernButton(tk.Button):
    """Botão moderno com hover"""
    def __init__(self, parent, text="", variant="primary", theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        variants = {
            'primary': {'bg': self.theme.PRIMARY, 'fg': 'white', 'hover': self.theme.PRIMARY_DARK},
            'secondary': {'bg': self.theme.BG_TERTIARY, 'fg': self.theme.TEXT_PRIMARY, 'hover': self.theme.BORDER},
            'success': {'bg': self.theme.SUCCESS, 'fg': 'white', 'hover': '#059669'},
            'danger': {'bg': self.theme.DANGER, 'fg': 'white', 'hover': '#dc2626'},
        }
        v = variants.get(variant, variants['primary'])
        config = {
            'text': text,
            'font': self.theme.get_font("md", "bold"),
            'bg': v['bg'],
            'fg': v['fg'],
            'activebackground': v['hover'],
            'activeforeground': v['fg'],
            'relief': 'flat',
            'borderwidth': 0,
            'padx': 20,
            'pady': 10,
            'cursor': 'hand2',
        }
        config.update(kwargs)
        super().__init__(parent, **config)
        self.default_bg = config['bg']
        self.hover_bg = v['hover']
        self.bind('<Enter>', lambda e: self.configure(bg=self.hover_bg))
        self.bind('<Leave>', lambda e: self.configure(bg=self.default_bg))


class StatusBadge(tk.Label):
    """Badge de status colorido"""
    def __init__(self, parent, text="", status="info", theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        status_colors = {
            'success': {'bg': self.theme.SUCCESS_BG, 'fg': self.theme.SUCCESS},
            'warning': {'bg': self.theme.WARNING_BG, 'fg': self.theme.WARNING},
            'danger': {'bg': self.theme.DANGER_BG, 'fg': self.theme.DANGER},
            'error': {'bg': '#fee2e2', 'fg': '#dc2626'},  # Vermelho para erro
            'info': {'bg': self.theme.INFO_BG, 'fg': self.theme.INFO},
        }
        colors = status_colors.get(status, status_colors['info'])
        config = {
            'text': text,
            'font': self.theme.get_font("sm", "bold"),
            'bg': colors['bg'],
            'fg': colors['fg'],
            'padx': 12,
            'pady': 4,
            'relief': 'flat',
        }
        config.update(kwargs)
        super().__init__(parent, **config)


class ScrollableFrame(tk.Frame):
    """Frame com scroll automático"""
    def __init__(self, parent, theme=None, **kwargs):
        self.theme = theme or ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY, **kwargs)
        
        # Canvas e scrollbar
        self.canvas = tk.Canvas(self, bg=self.theme.BG_SECONDARY, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.theme.BG_SECONDARY)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind mousewheel
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
    
    def get_frame(self):
        """Retorna o frame onde adicionar widgets"""
        return self.scrollable_frame


class MetricCard(tk.Frame):
    """Card de métrica com ícone"""
    def __init__(self, parent, icon="", title="", value="", variant="info", theme=None, command=None):
        self.theme = theme or ModernTheme()
        self.command = command
        
        super().__init__(
            parent,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
            cursor='hand2' if command else 'arrow'
        )
        
        container = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=20, pady=16)
        
        # Ícone
        icon_colors = {
            'success': self.theme.SUCCESS,
            'warning': self.theme.WARNING,
            'danger': self.theme.DANGER,
            'info': self.theme.INFO,
        }
        
        icon_label = tk.Label(
            container,
            text=icon,
            font=self.theme.get_font("xxl"),
            fg=icon_colors.get(variant, self.theme.INFO),
            bg=self.theme.BG_PRIMARY
        )
        icon_label.pack(anchor='w', pady=(0, 8))
        
        # Título
        title_label = tk.Label(
            container,
            text=title,
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        )
        title_label.pack(anchor='w')
        
        # Valor
        value_label = tk.Label(
            container,
            text=value,
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        )
        value_label.pack(anchor='w')
        
        # Configurar eventos de clique se houver comando
        if command:
            self._setup_click_bindings(container, icon_label, title_label, value_label)
    
    def _setup_click_bindings(self, *widgets):
        """Configura eventos de clique e hover"""
        def on_click(e):
            if self.command:
                self.command()
        
        def on_enter(e):
            self.configure(bg=self.theme.BG_HOVER, highlightbackground=self.theme.PRIMARY)
            for widget in widgets:
                widget.configure(bg=self.theme.BG_HOVER)
        
        def on_leave(e):
            self.configure(bg=self.theme.BG_PRIMARY, highlightbackground=self.theme.BORDER)
            for widget in widgets:
                widget.configure(bg=self.theme.BG_PRIMARY)
        
        # Bind em todos os widgets
        for widget in (self,) + widgets:
            widget.bind('<Button-1>', on_click)
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)


class TabButton(tk.Frame):
    """Botão de aba personalizado"""
    def __init__(self, parent, icon="", text="", theme=None, command=None, is_active=False, indent=False):
        self.theme = theme or ModernTheme()
        self.command = command
        self.is_active = is_active
        self.indent = indent
        
        super().__init__(
            parent,
            bg=self.theme.PRIMARY if is_active else self.theme.BG_PRIMARY,
            cursor='hand2',
            relief='flat'
        )
        
        # Padding ajustado para indentação
        padx_left = 32 if indent else 16
        
        container = tk.Frame(
            self,
            bg=self.theme.PRIMARY if is_active else self.theme.BG_PRIMARY
        )
        container.pack(fill='both', expand=True, padx=(padx_left, 16), pady=12)
        
        # Ícone
        self.icon_label = tk.Label(
            container,
            text=icon,
            font=self.theme.get_font("lg"),
            fg='white' if is_active else self.theme.TEXT_SECONDARY,
            bg=self.theme.PRIMARY if is_active else self.theme.BG_PRIMARY
        )
        self.icon_label.pack(side='left', padx=(0, 8))
        
        # Texto
        self.text_label = tk.Label(
            container,
            text=text,
            font=self.theme.get_font("md", "bold"),
            fg='white' if is_active else self.theme.TEXT_PRIMARY,
            bg=self.theme.PRIMARY if is_active else self.theme.BG_PRIMARY
        )
        self.text_label.pack(side='left')
        
        self._setup_bindings()
    
    def _setup_bindings(self):
        """Configura eventos de mouse"""
        def on_enter(e):
            if not self.is_active:
                self.configure(bg=self.theme.BG_HOVER)
                for widget in self.winfo_children():
                    widget.configure(bg=self.theme.BG_HOVER)
                    for child in widget.winfo_children():
                        child.configure(bg=self.theme.BG_HOVER)
        
        def on_leave(e):
            if not self.is_active:
                self.configure(bg=self.theme.BG_PRIMARY)
                for widget in self.winfo_children():
                    widget.configure(bg=self.theme.BG_PRIMARY)
                    for child in widget.winfo_children():
                        child.configure(bg=self.theme.BG_PRIMARY)
        
        def on_click(e):
            if self.command:
                self.command()
        
        # Aplica bindings em todos os widgets
        widgets = [self] + list(self.winfo_children())
        for widget in widgets:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.bind('<Button-1>', on_click)
            for child in widget.winfo_children():
                child.bind('<Enter>', on_enter)
                child.bind('<Leave>', on_leave)
                child.bind('<Button-1>', on_click)
    
    def set_active(self, active):
        """Define estado ativo/inativo"""
        self.is_active = active
        bg = self.theme.PRIMARY if active else self.theme.BG_PRIMARY
        fg = 'white' if active else self.theme.TEXT_PRIMARY
        fg_icon = 'white' if active else self.theme.TEXT_SECONDARY
        
        self.configure(bg=bg)
        for widget in self.winfo_children():
            widget.configure(bg=bg)
        self.icon_label.configure(bg=bg, fg=fg_icon)
        self.text_label.configure(bg=bg, fg=fg)


class ExpandableMenuItem(tk.Frame):
    """Menu item expansível com subitens"""
    def __init__(self, parent, icon="", text="", theme=None, subitems=None, on_subitem_click=None):
        self.theme = theme or ModernTheme()
        self.subitems = subitems or []
        self.on_subitem_click = on_subitem_click
        self.is_expanded = False
        self.subitem_frames = []
        
        super().__init__(parent, bg=self.theme.BG_PRIMARY)
        
        # Header do menu (clicável para expandir/colapsar)
        self.header = tk.Frame(self, bg=self.theme.BG_PRIMARY, cursor='hand2')
        self.header.pack(fill='x')
        
        header_content = tk.Frame(self.header, bg=self.theme.BG_PRIMARY)
        header_content.pack(fill='x', padx=16, pady=12)
        
        # Ícone de expansão
        self.expand_icon = tk.Label(
            header_content,
            text="▶",
            font=self.theme.get_font("xs"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        )
        self.expand_icon.pack(side='left', padx=(0, 8))
        
        # Ícone principal
        tk.Label(
            header_content,
            text=icon,
            font=self.theme.get_font("lg"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 8))
        
        # Texto
        tk.Label(
            header_content,
            text=text,
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        # Badge com contagem
        if self.subitems:
            tk.Label(
                header_content,
                text=str(len(self.subitems)),
                font=self.theme.get_font("xs", "bold"),
                fg='white',
                bg=self.theme.TEXT_SECONDARY,
                padx=6,
                pady=2
            ).pack(side='right')
        
        # Container para subitens (inicialmente escondido)
        self.subitems_container = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        
        # Bindings no header
        for widget in [self.header, header_content, self.expand_icon]:
            widget.bind('<Button-1>', lambda e: self._toggle_expand())
            widget.bind('<Enter>', lambda e: self.header.configure(bg=self.theme.BG_HOVER))
            widget.bind('<Leave>', lambda e: self.header.configure(bg=self.theme.BG_PRIMARY))
    
    def _toggle_expand(self):
        """Expande ou colapsa o menu"""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.expand_icon.configure(text="▼")
            self.subitems_container.pack(fill='x', pady=(0, 4))
            self._build_subitems()
        else:
            self.expand_icon.configure(text="▶")
            self.subitems_container.pack_forget()
    
    def _build_subitems(self):
        """Constrói lista de subitens"""
        # Limpa subitens antigos
        for widget in self.subitems_container.winfo_children():
            widget.destroy()
        self.subitem_frames.clear()
        
        for item in self.subitems:
            subitem = tk.Frame(
                self.subitems_container,
                bg=self.theme.BG_SECONDARY,
                cursor='hand2'
            )
            subitem.pack(fill='x', padx=(32, 0), pady=1)
            
            content = tk.Frame(subitem, bg=self.theme.BG_SECONDARY)
            content.pack(fill='x', padx=12, pady=8)
            
            # Ícone do subitem
            tk.Label(
                content,
                text="📄",
                font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_SECONDARY,
                bg=self.theme.BG_SECONDARY
            ).pack(side='left', padx=(0, 8))
            
            # Nome do job
            tk.Label(
                content,
                text=item.get('job', 'Sem nome'),
                font=self.theme.get_font("sm"),
                fg=self.theme.TEXT_PRIMARY,
                bg=self.theme.BG_SECONDARY,
                anchor='w'
            ).pack(side='left', fill='x', expand=True)
            
            # Badge de status
            status = "✓" if item.get('ativo') == 'S' else "✗"
            status_color = self.theme.SUCCESS if item.get('ativo') == 'S' else self.theme.DANGER
            tk.Label(
                content,
                text=status,
                font=self.theme.get_font("sm"),
                fg=status_color,
                bg=self.theme.BG_SECONDARY
            ).pack(side='right')
            
            # Bindings
            def make_click_handler(job_data):
                return lambda e: self.on_subitem_click(job_data) if self.on_subitem_click else None
            
            for widget in [subitem, content]:
                widget.bind('<Button-1>', make_click_handler(item))
                widget.bind('<Enter>', lambda e, f=subitem: f.configure(bg=self.theme.BG_HOVER))
                widget.bind('<Leave>', lambda e, f=subitem: f.configure(bg=self.theme.BG_SECONDARY))
            
            self.subitem_frames.append(subitem)
    
    def update_subitems(self, subitems):
        """Atualiza lista de subitens dinamicamente"""
        self.subitems = subitems
        if self.is_expanded:
            self._build_subitems()


# ==================== TOAST NOTIFICATION ====================

class Toast:
    """Sistema de notificações Toast moderno e não-bloqueante"""
    
    # Container global para toasts
    _toast_container = None
    _toast_queue = []
    _current_toasts = []
    _max_toasts = 3
    
    @staticmethod
    def _get_container(root):
        """Obtém ou cria o container de toasts"""
        if Toast._toast_container is None:
            # Container fixo no canto superior direito
            Toast._toast_container = tk.Frame(
                root,
                bg='',  # Transparente
            )
            Toast._toast_container.place(relx=1.0, rely=0.0, x=-20, y=20, anchor='ne')
            # Trazer para frente
            Toast._toast_container.lift()
        else:
            # Sempre garantir que está na frente
            Toast._toast_container.lift()
        return Toast._toast_container
    
    @staticmethod
    def show(root, message, title="", toast_type="info", duration=3000):
        """
        Exibe uma notificação toast
        
        Args:
            root: Janela principal
            message: Mensagem a ser exibida
            title: Título opcional
            toast_type: "success", "error", "warning", "info"
            duration: Duração em ms (0 = permanente)
        """
        try:
            print(f"[DEBUG] Toast.show called: type={toast_type}, title='{title}', message='{message[:50]}...'")
            
            theme = ModernTheme()
            
            # Configurações por tipo
            configs = {
                "success": {
                    "icon": "✓",
                    "bg": theme.SUCCESS,
                    "fg": "white",
                    "title_default": "Sucesso"
                },
                "error": {
                    "icon": "✗",
                    "bg": theme.DANGER,
                    "fg": "white",
                    "title_default": "Erro"
                },
                "warning": {
                    "icon": "⚠",
                    "bg": theme.WARNING,
                    "fg": "white",
                    "title_default": "Atenção"
                },
                "info": {
                    "icon": "ℹ",
                    "bg": theme.INFO,
                    "fg": "white",
                    "title_default": "Informação"
                }
            }
            
            config = configs.get(toast_type, configs["info"])
            
            # Usar título padrão se não fornecido
            if not title:
                title = config["title_default"]
            
            # Obter container
            container = Toast._get_container(root)
            
            print(f"[DEBUG] Container obtained: {container}")
            
            # Criar toast frame com borda para simular sombra
            toast_frame = tk.Frame(
                container,
                bg=config["bg"],
                relief='raised',
                borderwidth=2,
                highlightthickness=0
            )
            
            print(f"[DEBUG] Toast frame created")
            
            # Conteúdo do toast
            content = tk.Frame(toast_frame, bg=config["bg"])
            content.pack(fill='both', expand=True, padx=16, pady=12)
            
            # Linha 1: Ícone + Título + Botão fechar
            header = tk.Frame(content, bg=config["bg"])
            header.pack(fill='x', pady=(0, 4) if message else 0)
            
            # Ícone
            tk.Label(
                header,
                text=config["icon"],
                font=theme.get_font("lg", "bold"),
                fg=config["fg"],
                bg=config["bg"]
            ).pack(side='left', padx=(0, 8))
            
            # Título
            tk.Label(
                header,
                text=title,
                font=theme.get_font("md", "bold"),
                fg=config["fg"],
                bg=config["bg"]
            ).pack(side='left')
            
            # Botão fechar
            close_btn = tk.Label(
                header,
                text="✕",
                font=theme.get_font("md"),
                fg=config["fg"],
                bg=config["bg"],
                cursor='hand2'
            )
            close_btn.pack(side='right')
            
            # Mensagem (se fornecida)
            if message:
                tk.Label(
                    content,
                    text=message,
                    font=theme.get_font("sm"),
                    fg=config["fg"],
                    bg=config["bg"],
                    wraplength=300,
                    justify='left'
                ).pack(fill='x')
            
            # Função para fechar toast
            def close_toast():
                try:
                    # Animação de fade out
                    Toast._fade_out(toast_frame, lambda: Toast._remove_toast(toast_frame))
                except:
                    pass
            
            # Bind no botão fechar
            close_btn.bind('<Button-1>', lambda e: close_toast())
            
            # Gerenciar fila de toasts
            if len(Toast._current_toasts) >= Toast._max_toasts:
                # Remover o mais antigo
                oldest = Toast._current_toasts.pop(0)
                try:
                    oldest.destroy()
                except:
                    pass
        
            # Adicionar à lista de toasts ativos
            Toast._current_toasts.append(toast_frame)
            
            # Posicionar toast
            y_offset = sum(t.winfo_reqheight() + 8 for t in Toast._current_toasts[:-1])
            
            # Posicionar toast
            toast_frame.place(x=0, y=y_offset, width=350, height=0)
            
            # Trazer para frente (importante!)
            toast_frame.lift()
            container.lift()
            
            # Atualizar para obter dimensões reais
            toast_frame.update_idletasks()
            
            # Animação de entrada (slide in)
            Toast._slide_in(toast_frame)
            
            # Auto-fechar após duração (se não for 0)
            if duration > 0:
                root.after(duration, close_toast)
                
            print(f"[DEBUG] Toast displayed successfully")
            
        except Exception as e:
            print(f"[ERROR] Toast.show failed: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def _slide_in(toast_frame):
        """Animação de entrada"""
        target_height = toast_frame.winfo_reqheight()
        
        def animate(step=0):
            if step <= 10:
                current_height = int(target_height * (step / 10))
                toast_frame.place_configure(height=current_height)
                toast_frame.after(20, lambda: animate(step + 1))
            else:
                toast_frame.place_configure(height=target_height)
        
        animate()
    
    @staticmethod
    def _fade_out(toast_frame, callback):
        """Animação de saída"""
        def animate(step=10):
            if step >= 0:
                # Reduzir altura
                current_height = int(toast_frame.winfo_height() * (step / 10))
                toast_frame.place_configure(height=current_height)
                toast_frame.after(20, lambda: animate(step - 1))
            else:
                callback()
        
        animate()
    
    @staticmethod
    def _remove_toast(toast_frame):
        """Remove toast e reorganiza os demais"""
        try:
            if toast_frame in Toast._current_toasts:
                Toast._current_toasts.remove(toast_frame)
            toast_frame.destroy()
            
            # Reorganizar toasts restantes
            for i, toast in enumerate(Toast._current_toasts):
                y_offset = sum(t.winfo_reqheight() + 8 for t in Toast._current_toasts[:i])
                toast.place_configure(y=y_offset)
        except:
            pass
    
    @staticmethod
    def success(root, message, title="", duration=3000):
        """Toast de sucesso"""
        Toast.show(root, message, title, "success", duration)
    
    @staticmethod
    def error(root, message, title="", duration=5000):
        """Toast de erro (duração maior)"""
        Toast.show(root, message, title, "error", duration)
    
    @staticmethod
    def warning(root, message, title="", duration=4000):
        """Toast de aviso"""
        Toast.show(root, message, title, "warning", duration)
    
    @staticmethod
    def info(root, message, title="", duration=3000):
        """Toast de informação"""
        Toast.show(root, message, title, "info", duration)
