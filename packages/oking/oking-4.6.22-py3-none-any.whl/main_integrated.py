"""
🏢 Dashboard Principal Integrado - OKING Hub
Sistema completo com todas as telas integradas
"""
import tkinter as tk
from tkinter import messagebox, ttk
from ui_components import (
    ModernTheme, Card, ModernButton, StatusBadge, 
    MetricCard, TabButton, ScrollableFrame
)

# Importar versão
try:
    from src import __version__
except:
    __version__ = "0.0.0"

# Importar screens (Settings já está integrado)
try:
    from screens.settings import SettingsScreen
    SETTINGS_AVAILABLE = True
except:
    SETTINGS_AVAILABLE = False

try:
    from screens.help import HelpScreen
    HELP_AVAILABLE = True
except:
    HELP_AVAILABLE = False

try:
    from screens.logs import LogsScreen
    LOGS_AVAILABLE = True
except:
    LOGS_AVAILABLE = False

try:
    from screens.jobs import JobsScreen
    JOBS_AVAILABLE = True
except:
    JOBS_AVAILABLE = False

try:
    from screens.database import DatabaseScreen
    DATABASE_AVAILABLE = True
except:
    DATABASE_AVAILABLE = False

try:
    from screens.tokens import TokensScreen
    TOKENS_AVAILABLE = True
except:
    TOKENS_AVAILABLE = False

try:
    from screens.photos import PhotosScreen
    PHOTOS_AVAILABLE = True
except:
    PHOTOS_AVAILABLE = False


# ==================== DASHBOARD PRINCIPAL ====================

class IntegratedDashboard:
    """Dashboard principal com todas as telas integradas"""
    
    def __init__(self, root, shortname="", token_manager=None, jobs_data=None):
        self.root = root
        self.theme = ModernTheme()  # Será atualizado por _load_saved_settings
        self.current_tab = None
        self.tab_buttons = {}
        self.screen_instances = {}
        self.shortname = shortname
        self.token_manager = token_manager
        self.jobs_data = jobs_data or []
        self.selected_job_btn = None  # Rastreia botão de job selecionado
        
        # Carrega configurações salvas
        self._load_saved_settings()
        
        self._setup_window()
        self._build_ui()
        self._switch_tab("overview")
    
    def _load_saved_settings(self):
        """Carrega configurações salvas ao iniciar"""
        try:
            from pathlib import Path
            import json
            
            config_file = Path.home() / '.oking' / 'settings.json'
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    appearance = settings.get('appearance', {})
                    
                    # Aplica tema (light/dark/auto)
                    theme_mode = appearance.get('theme', 'light')
                    
                    # Por enquanto, 'auto' usa 'light'
                    if theme_mode == 'auto':
                        theme_mode = 'light'
                    
                    # Carrega tamanho da fonte e modo compacto
                    font_size = appearance.get('font_size', 12)
                    compact_mode = appearance.get('compact_mode', False)
                    
                    # Cria tema com configurações
                    self.theme = ModernTheme(mode=theme_mode, base_font_size=font_size, compact_mode=compact_mode)
                    
                    # Aplica cor primária
                    if 'primary_color' in appearance:
                        self.theme.PRIMARY = appearance['primary_color']
                        # Calcula variações
                        hex_color = appearance['primary_color'].lstrip('#')
                        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
                        
                        # Dark
                        rd, gd, bd = max(0, int(r * 0.8)), max(0, int(g * 0.8)), max(0, int(b * 0.8))
                        self.theme.PRIMARY_DARK = f'#{rd:02x}{gd:02x}{bd:02x}'
                        
                        # Light
                        rl, gl, bl = min(255, int(r * 1.2)), min(255, int(g * 1.2)), min(255, int(b * 1.2))
                        self.theme.PRIMARY_LIGHT = f'#{rl:02x}{gl:02x}{bl:02x}'
            else:
                # Nenhuma configuração salva, usa padrão light
                self.theme = ModernTheme(mode='light', base_font_size=12, compact_mode=False)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            self.theme = ModernTheme(mode='light', base_font_size=12, compact_mode=False)
    
    def _setup_window(self):
        self.root.title(f"🏢 OKING Hub - Sistema de Integração v{__version__}")
        w, h = 1400, 900
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.root.configure(bg=self.theme.BG_SECONDARY)
        
        # Definir ícone da janela
        self._set_window_icon()
    
    def _set_window_icon(self):
        """Define o ícone da janela"""
        try:
            from pathlib import Path
            
            # Procurar por icon.ico ou icon.png na raiz do projeto
            icon_paths = [
                Path(__file__).parent / 'icon.ico',
                Path(__file__).parent / 'assets' / 'icon.ico',
                Path(__file__).parent / 'icon.png',
                Path(__file__).parent / 'assets' / 'icon.png',
            ]
            
            for icon_path in icon_paths:
                if icon_path.exists():
                    if icon_path.suffix == '.ico':
                        self.root.iconbitmap(str(icon_path))
                    elif icon_path.suffix == '.png':
                        from PIL import Image, ImageTk
                        img = Image.open(icon_path)
                        photo = ImageTk.PhotoImage(img)
                        self.root.iconphoto(True, photo)
                    print(f"[INFO] Ícone carregado: {icon_path}")
                    return
            
            print("[INFO] Nenhum arquivo de ícone encontrado - usando ícone padrão")
            
        except Exception as e:
            print(f"[WARN] Erro ao carregar ícone: {e}")
    
    def _build_ui(self):
        # Container principal
        main_container = tk.Frame(self.root, bg=self.theme.BG_SECONDARY)
        main_container.pack(fill='both', expand=True)
        
        # Header fixo
        self._build_header(main_container)
        
        # Conteúdo (sidebar + área principal)
        content = tk.Frame(main_container, bg=self.theme.BG_SECONDARY)
        content.pack(fill='both', expand=True)
        
        # Sidebar de navegação
        self._build_sidebar(content)
        
        # Área de conteúdo
        padding = self.theme.SPACING_LG
        self.content_area = tk.Frame(content, bg=self.theme.BG_SECONDARY)
        self.content_area.pack(side='left', fill='both', expand=True, padx=(0, padding), pady=(0, padding))
    
    def _build_header(self, parent):
        """Cabeçalho fixo"""
        header = Card(parent, theme=self.theme)
        padding = self.theme.SPACING_LG
        header.pack(fill='x', padx=padding, pady=padding)
        
        container = tk.Frame(header, bg=self.theme.BG_PRIMARY)
        inner_padding = self.theme.SPACING_MD
        container.pack(fill='x', padx=inner_padding + 4, pady=inner_padding)
        
        # Esquerda
        left = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        left.pack(side='left', fill='x', expand=True)
        
        tk.Label(
            left,
            text="🏢 OKING Hub",
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(0, 16))
        
        # Mostrar shortname se disponível
        if self.shortname:
            tk.Label(
                left,
                text=f"📦 {self.shortname.upper()}",
                font=self.theme.get_font("lg", "bold"),
                fg=self.theme.TEXT_PRIMARY,
                bg=self.theme.BG_PRIMARY
            ).pack(side='left', padx=(0, 16))
        
        # Mostrar token ativo se disponível
        if self.token_manager:
            try:
                active_token = self.token_manager.get_active_token()
                if active_token and 'nome' in active_token:
                    token_frame = tk.Frame(left, bg=self.theme.SUCCESS_BG, relief='flat', bd=1)
                    token_frame.pack(side='left', padx=(0, 8))
                    
                    # ✅ Salvar referência do label para poder atualizar depois
                    self.token_label = tk.Label(
                        token_frame,
                        text=f"🔑 Token: {active_token['nome']}",
                        font=self.theme.get_font("sm", "bold"),
                        fg=self.theme.SUCCESS,
                        bg=self.theme.SUCCESS_BG
                    )
                    self.token_label.pack(padx=12, pady=6)
                    
                    # Salvar também referência do frame para poder recriar se necessário
                    self.token_frame = token_frame
            except:
                pass
        
        # Mostrar versão
        version_frame = tk.Frame(left, bg=self.theme.BG_HOVER, relief='flat', bd=1)
        version_frame.pack(side='left')
        
        tk.Label(
            version_frame,
            text=f"v{__version__}",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_HOVER
        ).pack(padx=12, pady=6)
        
        # Direita
        right = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        right.pack(side='right')
        
        ModernButton(
            right,
            text="⚙️ Configurações",
            variant="secondary",
            theme=self.theme,
            command=lambda: self._switch_tab("settings")
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            right,
            text="❓ Ajuda",
            variant="secondary",
            theme=self.theme,
            command=lambda: self._switch_tab("help")
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            right,
            text="🚪 Sair",
            variant="danger",
            theme=self.theme,
            command=self._confirm_exit
        ).pack(side='left')
    
    def _build_sidebar(self, parent):
        """Sidebar de navegação"""
        sidebar = Card(parent, theme=self.theme)
        sidebar.pack(side='left', fill='y', padx=(24, 12), pady=(0, 24))
        sidebar.pack_propagate(False)
        sidebar.configure(width=280)
        
        # Canvas + Scrollbar para permitir scroll
        canvas = tk.Canvas(
            sidebar,
            bg=self.theme.BG_PRIMARY,
            highlightthickness=0,
            width=268  # Largura fixa para não expandir
        )
        scrollbar = ttk.Scrollbar(sidebar, orient='vertical', command=canvas.yview)
        
        container = tk.Frame(canvas, bg=self.theme.BG_PRIMARY)
        
        # Criar window com width vinculado ao canvas
        canvas_window = canvas.create_window((0, 0), window=container, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y', padx=(0, 4))
        
        # Atualizar largura do container para seguir o canvas
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Configurar scroll region
        container.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        # Adicionar mousewheel scroll apenas quando mouse está sobre o sidebar
        def on_enter(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def on_leave(event):
            canvas.unbind_all("<MouseWheel>")
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        sidebar.bind('<Enter>', on_enter)
        sidebar.bind('<Leave>', on_leave)
        
        # Título
        tk.Label(
            container,
            text="📋 Navegação",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', padx=12, pady=(8, 16))
        
        # Abas principais (antes de jobs)
        overview_btn = TabButton(
            container,
            icon="🏠",
            text="Visão Geral",
            theme=self.theme,
            command=lambda: self._switch_tab("overview"),
            is_active=True
        )
        overview_btn.pack(fill='x', pady=(0, 4))
        self.tab_buttons["overview"] = overview_btn
        
        # Variável de controle para expandir/recolher jobs
        self.jobs_expanded = tk.BooleanVar(value=False)
        
        # Botão toggle para Configurar Jobs (usando TabButton para manter o estilo)
        self.jobs_toggle_btn = TabButton(
            container,
            icon="▶",
            text="Configurar Jobs",
            theme=self.theme,
            command=self._toggle_jobs_menu,
            is_active=False
        )
        self.jobs_toggle_btn.pack(fill='x', pady=(0, 4))
        self.tab_buttons["jobs"] = self.jobs_toggle_btn
        
        # Container para lista de jobs (criado logo após o botão, mas inicialmente oculto)
        self.jobs_menu_container = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        # NÃO fazer pack aqui - será feito no _toggle_jobs_menu quando expandir
        
        # Carregar lista de jobs para o submenu (popula o container)
        self._load_jobs_submenu()
        
        # Demais abas principais
        remaining_tabs = [
            {"id": "database", "icon": "🗄️", "text": "Banco de Dados"},
            {"id": "tokens", "icon": "🔑", "text": "Tokens"},
            {"id": "logs", "icon": "📝", "text": "Logs"},
            {"id": "settings", "icon": "🎨", "text": "Tema"},
            {"id": "help", "icon": "❓", "text": "Ajuda"},
        ]
        
        for tab in remaining_tabs:
            btn = TabButton(
                container,
                icon=tab["icon"],
                text=tab["text"],
                theme=self.theme,
                command=lambda t=tab["id"]: self._switch_tab(t),
                is_active=False
            )
            btn.pack(fill='x', pady=(0, 4))
            self.tab_buttons[tab["id"]] = btn
        
        # Separador
        tk.Frame(container, bg=self.theme.BORDER, height=1).pack(fill='x', pady=8)
        
        # Variável de controle para expandir/recolher adicionais
        self.adicionais_expanded = tk.BooleanVar(value=False)
        
        # Botão toggle para Adicionais (usando TabButton para manter o estilo)
        self.adicionais_toggle_btn = TabButton(
            container,
            icon="▶",
            text="Adicionais",
            theme=self.theme,
            command=self._toggle_adicionais,
            is_active=False
        )
        self.adicionais_toggle_btn.pack(fill='x', pady=(0, 4))
        
        # Container para subitens de Adicionais (inicialmente oculto)
        self.adicionais_container = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        
        # Submenu de adicionais
        photos_btn = tk.Button(
            self.adicionais_container,
            text="    ⚙️ Upload de Fotos",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY,
            activebackground=self.theme.BG_HOVER,
            activeforeground=self.theme.TEXT_PRIMARY,
            relief='flat',
            cursor='hand2',
            anchor='w',
            padx=12,
            pady=8,
            command=lambda: self._switch_tab("photos")
        )
        photos_btn.pack(fill='x')
        
        # Hover effect para Photos
        def on_enter_photos(e):
            if photos_btn != self.selected_job_btn:
                photos_btn.configure(bg=self.theme.BG_HOVER, fg=self.theme.TEXT_PRIMARY)
        
        def on_leave_photos(e):
            if photos_btn != self.selected_job_btn:
                photos_btn.configure(bg=self.theme.BG_PRIMARY, fg=self.theme.TEXT_SECONDARY)
        
        photos_btn.bind('<Enter>', on_enter_photos)
        photos_btn.bind('<Leave>', on_leave_photos)
        self.tab_buttons["photos"] = photos_btn
    
    def _switch_tab(self, tab_id):
        """Troca de aba"""
        if self.current_tab == tab_id:
            return
        
        self.current_tab = tab_id
        
        # Atualiza botões (apenas TabButtons têm set_active)
        for tid, btn in self.tab_buttons.items():
            if hasattr(btn, 'set_active'):
                btn.set_active(tid == tab_id)
            else:
                # Para botões simples do submenu
                if tid == tab_id:
                    btn.configure(bg=self.theme.BG_HOVER, fg=self.theme.PRIMARY)
                else:
                    btn.configure(bg=self.theme.BG_PRIMARY, fg=self.theme.TEXT_SECONDARY)
        
        # Limpar seleção de job se mudando para outra aba que não seja jobs
        if tab_id != "jobs" and self.selected_job_btn and self.selected_job_btn.winfo_exists():
            self.selected_job_btn.configure(
                bg=self.theme.BG_PRIMARY,
                fg=self.theme.TEXT_SECONDARY
            )
            self.selected_job_btn = None
        
        # Limpa área de conteúdo
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Renderiza conteúdo
        if tab_id == "overview":
            self._render_overview()
        elif tab_id == "jobs":
            self._load_screen("jobs", self._create_jobs_screen)
        elif tab_id == "database":
            self._load_screen("database", self._create_database_screen)
        elif tab_id == "tokens":
            self._load_screen("tokens", self._create_tokens_screen)
        elif tab_id == "photos":
            self._load_screen("photos", self._create_photos_screen)
        elif tab_id == "logs":
            self._load_screen("logs", self._create_logs_screen)
        elif tab_id == "settings":
            self._load_screen("settings", self._create_settings_screen)
        elif tab_id == "help":
            self._load_screen("help", self._create_help_screen)
    
    def _toggle_adicionais(self):
        """Toggle do submenu Adicionais"""
        self.adicionais_expanded.set(not self.adicionais_expanded.get())
        
        if self.adicionais_expanded.get():
            # Expandir: mudar ícone para ▼
            self.adicionais_toggle_btn.icon_label.configure(text="▼")
            # Pack após o botão de adicionais
            next_widget = None
            found_adicionais_btn = False
            for widget in self.adicionais_toggle_btn.master.winfo_children():
                if found_adicionais_btn and widget != self.adicionais_container:
                    next_widget = widget
                    break
                if widget == self.adicionais_toggle_btn:
                    found_adicionais_btn = True
            
            if next_widget:
                self.adicionais_container.pack(fill='x', before=next_widget)
            else:
                self.adicionais_container.pack(fill='x')
        else:
            # Recolher: mudar ícone para ▶
            self.adicionais_toggle_btn.icon_label.configure(text="▶")
            self.adicionais_container.pack_forget()
    
    def _toggle_jobs_menu(self):
        """Toggle do submenu Configurar Jobs"""
        self.jobs_expanded.set(not self.jobs_expanded.get())
        
        if self.jobs_expanded.get():
            # Expandir: mudar ícone para ▼
            self.jobs_toggle_btn.icon_label.configure(text="▼")
            # Pack após o botão de jobs (antes do próximo widget)
            next_widget = None
            found_jobs_btn = False
            for widget in self.jobs_toggle_btn.master.winfo_children():
                if found_jobs_btn and widget != self.jobs_menu_container:
                    next_widget = widget
                    break
                if widget == self.jobs_toggle_btn:
                    found_jobs_btn = True
            
            if next_widget:
                self.jobs_menu_container.pack(fill='x', before=next_widget)
            else:
                self.jobs_menu_container.pack(fill='x')
        else:
            # Recolher: mudar ícone para ▶
            self.jobs_toggle_btn.icon_label.configure(text="▶")
            self.jobs_menu_container.pack_forget()
    
    def _load_jobs_submenu(self):
        """Carrega lista de jobs no submenu"""
        try:
            # Buscar jobs da API
            if not self.token_manager:
                return
            
            # Obtém URL base
            base_url = self.token_manager.get_base_url()
            if not base_url:
                return
            
            active_token = self.token_manager.get_active_token()
            if not active_token:
                return
            
            import urllib.request
            import urllib.parse
            import json
            
            url = f"https://{base_url}/api/consulta/oking_hub/filtros"
            params = {"token": active_token['token']}
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Obter lista de jobs do campo 'modulos'
                jobs = data.get('modulos', [])
                
                # Limpar container antes de adicionar novos itens
                for widget in self.jobs_menu_container.winfo_children():
                    widget.destroy()
                
                # Adicionar cada job como submenu item
                if jobs:
                    for job in jobs:
                        job_name = job.get('job') or job.get('nome_job', 'Job sem nome')
                        is_active = job.get('ativo') == 'S'
                        
                        # Definir cores baseadas no status
                        if is_active:
                            text_color = self.theme.TEXT_SECONDARY
                            icon = "⚙️"
                        else:
                            text_color = "#e57373"  # Cor avermelhada para inativo
                            icon = "⭕"  # Ícone diferente para inativo
                        
                        job_btn = tk.Button(
                            self.jobs_menu_container,
                            text=f"    {icon} {job_name}",
                            font=self.theme.get_font("sm"),
                            fg=text_color,
                            bg=self.theme.BG_PRIMARY,
                            activebackground=self.theme.BG_HOVER,
                            activeforeground=self.theme.TEXT_PRIMARY,
                            relief='flat',
                            cursor='hand2',
                            anchor='w',
                            padx=12,
                            pady=8
                        )
                        job_btn.pack(fill='x')
                        
                        # Configurar comando após criação
                        job_btn.configure(command=lambda jn=job_name, btn=job_btn: self._go_to_job_config(jn, btn))
                        
                        # Hover effect (preserva cor original ao sair)
                        def on_enter(e, btn=job_btn):
                            # Se não é o selecionado, aplica hover
                            if btn != self.selected_job_btn:
                                btn.configure(bg=self.theme.BG_HOVER, fg=self.theme.TEXT_PRIMARY)
                        
                        def on_leave(e, btn=job_btn, original_color=text_color):
                            # Se não é o selecionado, remove hover (volta cor original)
                            if btn != self.selected_job_btn:
                                btn.configure(bg=self.theme.BG_PRIMARY, fg=original_color)
                        
                        job_btn.bind('<Enter>', on_enter)
                        job_btn.bind('<Leave>', on_leave)
                else:
                    # Sem jobs disponíveis
                    tk.Label(
                        self.jobs_menu_container,
                        text="    Nenhum job encontrado",
                        font=self.theme.get_font("sm"),
                        fg=self.theme.TEXT_TERTIARY,
                        bg=self.theme.BG_PRIMARY,
                        anchor='w',
                        padx=12,
                        pady=8
                    ).pack(fill='x')
                    
        except Exception as e:
            print(f"[ERROR] Erro ao carregar jobs no submenu: {e}")
            # Em caso de erro, mostrar mensagem
            tk.Label(
                self.jobs_menu_container,
                text="    ⚠️ Erro ao carregar jobs",
                font=self.theme.get_font("sm"),
                fg=self.theme.DANGER,
                bg=self.theme.BG_PRIMARY,
                anchor='w',
                padx=12,
                pady=8
            ).pack(fill='x')
    
    def _go_to_job_config(self, job_name, job_btn=None):
        """Navega para a tela de Jobs com job específico selecionado"""
        # Desselecionar botão anterior
        if self.selected_job_btn and self.selected_job_btn.winfo_exists():
            self.selected_job_btn.configure(
                bg=self.theme.BG_PRIMARY,
                fg=self.theme.TEXT_SECONDARY
            )
        
        # Selecionar novo botão
        if job_btn:
            self.selected_job_btn = job_btn
            job_btn.configure(
                bg=self.theme.BG_HOVER,
                fg=self.theme.PRIMARY
            )
        
        # Mudar para a aba de jobs
        self._switch_tab("jobs")
        
        # Aguardar 300ms para a tela ser completamente renderizada e carregar os jobs
        self.root.after(300, lambda: self._select_job_by_name(job_name))
    
    def _select_job_by_name(self, job_name):
        """Seleciona um job específico na tela de jobs"""
        jobs_screen = self.screen_instances.get("jobs")
        if jobs_screen and hasattr(jobs_screen, 'select_job_by_name'):
            jobs_screen.select_job_by_name(job_name)
    
    def _load_screen(self, screen_id, creator_func):
        """Carrega ou reutiliza tela"""
        # Cria nova instância toda vez (área de conteúdo já foi limpa)
        screen = creator_func()
        self.screen_instances[screen_id] = screen
        
        # Exibe a tela
        screen.pack(fill='both', expand=True)
    
    # ==================== CRIADORES DE TELAS ====================
    
    def _create_jobs_screen(self):
        """Cria tela de configuração de jobs"""
        if JOBS_AVAILABLE:
            return JobsScreen(self.content_area, shortname=self.shortname, token_manager=self.token_manager, theme=self.theme)
        return self._create_placeholder("⚙️ Configuração de Jobs", "Configure jobs de sincronização")
    
    def _create_database_screen(self):
        """Cria tela de banco de dados"""
        if DATABASE_AVAILABLE:
            return DatabaseScreen(self.content_area, shortname=self.shortname, token_manager=self.token_manager, theme=self.theme)
        return self._create_placeholder("🗄️ Configuração de Banco de Dados", "Configure conexões Oracle e SQL Server")
    
    def _create_tokens_screen(self):
        """Cria tela de tokens"""
        if TOKENS_AVAILABLE:
            screen = TokensScreen(self.content_area, token_manager=self.token_manager, theme=self.theme)
            # ✅ Adicionar callback para reload quando trocar token
            screen.on_token_changed = self._on_token_changed
            return screen
        return self._create_placeholder("🔑 Gerenciamento de Tokens", "Gerencie tokens de API")
    
    def _create_photos_screen(self):
        """Cria tela de fotos"""
        if PHOTOS_AVAILABLE:
            return PhotosScreen(self.content_area, theme=self.theme)
        return self._create_placeholder("📸 Upload de Fotos", "Envie fotos de produtos")
    
    def _create_logs_screen(self):
        """Cria tela de logs"""
        if LOGS_AVAILABLE:
            return LogsScreen(self.content_area, shortname=self.shortname, token_manager=self.token_manager, theme=self.theme)
        return self._create_placeholder("📝 Logs do Sistema", "Visualize logs de execução")
    
    def _create_settings_screen(self):
        """Cria tela de configurações"""
        if SETTINGS_AVAILABLE:
            return SettingsScreen(self.content_area, dashboard=self)
        return self._create_placeholder("🎨 Tema e Aparência", "Personalize a interface")
    
    def _create_help_screen(self):
        """Cria tela de ajuda"""
        if HELP_AVAILABLE:
            return HelpScreen(self.content_area, theme=self.theme)
        return self._create_placeholder("❓ Ajuda e Documentação", "Documentação e suporte")
    
    def _create_placeholder(self, title, description):
        """Cria placeholder para tela"""
        container = tk.Frame(self.content_area, bg=self.theme.BG_SECONDARY)
        
        card = Card(container, theme=self.theme)
        card.pack(fill='both', expand=True)
        
        content = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        content.pack(fill='both', expand=True, padx=40, pady=40)
        
        tk.Label(
            content,
            text=title,
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(pady=(40, 16))
        
        tk.Label(
            content,
            text=description,
            font=self.theme.get_font("lg"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(pady=(0, 40))
        
        ModernButton(
            content,
            text="🚀 Em breve disponível",
            variant="primary",
            theme=self.theme,
            command=lambda: messagebox.showinfo("Info", "Tela em desenvolvimento")
        ).pack()
        
        return container
    
    # ==================== VISÃO GERAL ====================
    
    def _render_overview(self):
        """Renderiza visão geral com dados reais da API"""
        scrollable = ScrollableFrame(self.content_area, theme=self.theme)
        scrollable.pack(fill='both', expand=True)
        
        content = scrollable.get_frame()
        
        # Título
        tk.Label(
            content,
            text="📊 Visão Geral do Sistema",
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_SECONDARY
        ).pack(anchor='w', pady=(0, 20))
        
        # Buscar dados reais
        jobs_data = self._get_jobs_stats()
        logs_data = self._get_logs_stats()
        recent_executions = self._get_recent_executions()  # Nova função para últimas execuções
        
        # LOG TEMPORÁRIO para diagnóstico
        print(f"\n=== DIAGNÓSTICO DASHBOARD ===")
        print(f"Jobs data: {jobs_data}")
        print(f"Logs data: {logs_data}")
        print(f"Recent executions: {len(recent_executions)} jobs")
        print(f"=============================\n")
        
        # Métricas
        metrics_container = tk.Frame(content, bg=self.theme.BG_SECONDARY)
        metrics_container.pack(fill='x', pady=(0, 24))
        
        metrics = [
            {"icon": "✅", "title": "Jobs Ativos", "value": str(jobs_data['ativos']), "variant": "success", "command": None},
            {"icon": "⏸️", "title": "Jobs Pausados", "value": str(jobs_data['pausados']), "variant": "warning", "command": None},
            {"icon": "🔄", "title": "Total de Jobs", "value": str(jobs_data['total']), "variant": "info", "command": None},
            {"icon": "⚠️", "title": "Erros Hoje", "value": str(logs_data['erros_hoje']), "variant": "danger", "command": self._go_to_errors},
        ]
        
        for i, metric in enumerate(metrics):
            card = MetricCard(
                metrics_container,
                icon=metric["icon"],
                title=metric["title"],
                value=metric["value"],
                variant=metric["variant"],
                theme=self.theme,
                command=metric["command"]
            )
            card.grid(row=0, column=i, padx=(0, 16) if i < len(metrics)-1 else (0, 0), sticky='ew')
            metrics_container.grid_columnconfigure(i, weight=1)
        
        # Últimas execuções
        tk.Label(
            content,
            text="🕒 Últimas Execuções",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY
        ).pack(anchor='w', pady=(0, 16))
        
        executions_card = Card(content, theme=self.theme)
        executions_card.pack(fill='x')
        
        # Container com scroll para suportar muitos jobs
        exec_wrapper = tk.Frame(executions_card, bg=self.theme.BG_PRIMARY)
        exec_wrapper.pack(fill='both', expand=True, padx=20, pady=16)
        
        # Canvas e Scrollbar
        canvas = tk.Canvas(
            exec_wrapper,
            bg=self.theme.BG_PRIMARY,
            highlightthickness=0,
            height=400  # Altura máxima
        )
        scrollbar = tk.Scrollbar(exec_wrapper, orient="vertical", command=canvas.yview)
        exec_container = tk.Frame(canvas, bg=self.theme.BG_PRIMARY)
        
        exec_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=exec_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Habilitar scroll com mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        if not recent_executions:
            tk.Label(
                exec_container,
                text="Nenhuma execução recente encontrada",
                font=self.theme.get_font("md"),
                fg=self.theme.TEXT_SECONDARY,
                bg=self.theme.BG_PRIMARY
            ).pack()
        else:
            for i, exec_data in enumerate(recent_executions):
                exec_frame = tk.Frame(exec_container, bg=self.theme.BG_PRIMARY)
                exec_frame.pack(fill='x', pady=(0, 16) if i < len(recent_executions)-1 else 0)
                
                # Linha 1: Nome do Job
                nome_frame = tk.Frame(exec_frame, bg=self.theme.BG_PRIMARY)
                nome_frame.pack(fill='x', pady=(0, 4))
                
                tk.Label(
                    nome_frame,
                    text=exec_data.get('nome_job', 'Job desconhecido'),
                    font=self.theme.get_font("md", "bold"),
                    fg=self.theme.TEXT_PRIMARY,
                    bg=self.theme.BG_PRIMARY
                ).pack(side='left')
                
                # Status badge (ativo/pausado)
                status_text = "✓ Ativo" if exec_data.get('ativo') else "⏸ Pausado"
                status_variant = "success" if exec_data.get('ativo') else "warning"
                StatusBadge(
                    nome_frame,
                    text=status_text,
                    status=status_variant,
                    theme=self.theme
                ).pack(side='right')
                
                # Linha 2: Informações de execução
                info_frame = tk.Frame(exec_frame, bg=self.theme.BG_PRIMARY)
                info_frame.pack(fill='x')
                
                # Intervalo de tempo
                intervalo = self._format_intervalo_tempo(exec_data.get('tempo_execucao', 0))
                tk.Label(
                    info_frame,
                    text=f"⏱ {intervalo}",
                    font=self.theme.get_font("sm"),
                    fg=self.theme.TEXT_SECONDARY,
                    bg=self.theme.BG_PRIMARY
                ).pack(side='left')
                
                # Separador
                tk.Label(
                    info_frame,
                    text="•",
                    font=self.theme.get_font("sm"),
                    fg=self.theme.TEXT_TERTIARY,
                    bg=self.theme.BG_PRIMARY
                ).pack(side='left', padx=8)
                
                # Última execução
                ultima_exec = exec_data.get('ultima_execucao_str', '')
                tk.Label(
                    info_frame,
                    text=f"📅 Última: {ultima_exec}",
                    font=self.theme.get_font("sm"),
                    fg=self.theme.TEXT_SECONDARY,
                    bg=self.theme.BG_PRIMARY
                ).pack(side='left')
                
                # Ações (à direita)
                actions_frame = tk.Frame(info_frame, bg=self.theme.BG_PRIMARY)
                actions_frame.pack(side='right')
                
                # Ícone "Exibir Logs"
                job_name = exec_data.get('nome_job', '')
                logs_btn = tk.Label(
                    actions_frame,
                    text="📋",
                    font=self.theme.get_font("md"),
                    fg=self.theme.PRIMARY,
                    bg=self.theme.BG_PRIMARY,
                    cursor="hand2"
                )
                logs_btn.pack(side='left', padx=(8, 4))
                
                # Tooltip
                self._create_tooltip(logs_btn, "Exibir Logs")
                
                # Comando para ir para logs
                logs_btn.bind('<Button-1>', lambda e, jn=job_name: self._go_to_logs_filtered(jn))
                
                # Ícone "Detalhes"
                details_btn = tk.Label(
                    actions_frame,
                    text="⚙️",
                    font=self.theme.get_font("md"),
                    fg=self.theme.PRIMARY,
                    bg=self.theme.BG_PRIMARY,
                    cursor="hand2"
                )
                details_btn.pack(side='left', padx=(4, 0))
                
                # Tooltip
                self._create_tooltip(details_btn, "Detalhes do Job")
                
                # Comando para ir para configuração do job
                details_btn.bind('<Button-1>', lambda e, jn=job_name: self._go_to_job_config(jn))
    
    def _get_jobs_stats(self):
        """Busca estatísticas de jobs da API"""
        try:
            print(f"\n[DEBUG] Iniciando _get_jobs_stats")
            print(f"[DEBUG] shortname: {self.shortname}")
            print(f"[DEBUG] token_manager: {self.token_manager}")
            
            if not self.token_manager:
                print(f"[DEBUG] Faltando token_manager")
                return {'total': 0, 'ativos': 0, 'pausados': 0}
            
            # Obtém URL base
            base_url = self.token_manager.get_base_url()
            if not base_url:
                print(f"[DEBUG] Faltando configuração de URL")
                return {'total': 0, 'ativos': 0, 'pausados': 0}
            
            active_token = self.token_manager.get_active_token()
            print(f"[DEBUG] active_token obtido: {active_token is not None}")
            
            if not active_token:
                print(f"[DEBUG] Sem token ativo")
                return {'total': 0, 'ativos': 0, 'pausados': 0}
            
            import urllib.request
            import urllib.parse
            import json
            
            token = active_token.get('token', '')
            url = f"https://{base_url}/api/consulta/oking_hub/filtros"
            params = urllib.parse.urlencode({'token': token})
            full_url = f"{url}?{params}"
            
            print(f"[DEBUG] URL: {url}")
            print(f"[DEBUG] Fazendo requisição...")
            
            req = urllib.request.Request(full_url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                print(f"[DEBUG] Resposta recebida")
                print(f"[DEBUG] Keys na resposta: {list(data.keys()) if isinstance(data, dict) else 'não é dict'}")
                
                # A API retorna diretamente os dados, sem campo 'sucesso'
                # Verifica se tem o campo 'modulos'
                if isinstance(data, dict) and 'modulos' in data:
                    jobs = data.get('modulos', [])
                    print(f"[DEBUG] Total de modulos: {len(jobs)}")
                    
                    if jobs:
                        print(f"[DEBUG] Primeiro job: {jobs[0].get('job')}, ativo={jobs[0].get('ativo')}")
                    
                    total = len(jobs)
                    
                    # Contar jobs ativos (ativo='S')
                    ativos = sum(1 for job in jobs if job.get('ativo') == 'S')
                    pausados = total - ativos
                    
                    print(f"[DEBUG] Resultado: total={total}, ativos={ativos}, pausados={pausados}")
                    
                    return {'total': total, 'ativos': ativos, 'pausados': pausados}
                else:
                    print(f"[DEBUG] Resposta não tem campo 'modulos'")
                    
        except Exception as e:
            print(f"[ERROR] Erro ao buscar stats de jobs: {e}")
            import traceback
            traceback.print_exc()
        
        return {'total': 0, 'ativos': 0, 'pausados': 0}
    
    def _get_logs_stats(self):
        """
        Busca estatísticas de logs da API
        
        IMPORTANTE: Este método usa o endpoint otimizado /api/consulta/log_estatisticas_dia/filtros
        que retorna contadores agregados (COUNT) ao invés de todos os logs.
        
        Endpoint esperado:
            GET /api/consulta/log_estatisticas_dia/filtros?token=XXX&data_inicio=YYYY-MM-DD
            
        Resposta esperada:
            {
                "erros": 16,
                "total": 43,
                "warnings": 0,
                "ultimo_erro": "2025-11-11 11:28:07.000000"
            }
        
        Retorno do método:
            {
                "erros_hoje": 16,
                "total_logs": 43,
                "total_warnings": 0
            }
        
        Fallback: Se o endpoint não existir (404), tenta usar o endpoint antigo /api/consulta/log/filtros
        mas com aviso de que a contagem pode estar incompleta.
        """
        try:
            print(f"\n[DEBUG] Iniciando _get_logs_stats")
            
            if not self.token_manager:
                print(f"[DEBUG] Logs: Faltando token_manager")
                return {'erros_hoje': 0}
            
            # Obtém URL base
            base_url = self.token_manager.get_base_url()
            if not base_url:
                print(f"[DEBUG] Logs: Faltando configuração de URL")
                return {'erros_hoje': 0}
            
            active_token = self.token_manager.get_active_token()
            if not active_token:
                print(f"[DEBUG] Logs: Sem token ativo")
                return {'erros_hoje': 0}
            
            import urllib.request
            import urllib.parse
            import urllib.error
            import json
            from datetime import datetime
            
            token = active_token.get('token', '')
            hoje = datetime.now().strftime('%Y-%m-%d')
            
            # ========================================
            # PASSO 1: Tentar endpoint OTIMIZADO (novo)
            # ========================================
            try:
                url_stats = f"https://{base_url}/api/consulta/log_estatisticas_dia/filtros"
                params = urllib.parse.urlencode({
                    'token': token,
                    'data_inicio': hoje
                })
                full_url_stats = f"{url_stats}?{params}"
                
                print(f"[DEBUG] Logs: Tentando endpoint otimizado: {url_stats}")
                
                req_stats = urllib.request.Request(full_url_stats)
                with urllib.request.urlopen(req_stats, timeout=10) as response:
                    response_data = response.read().decode('utf-8')
                    
                    # Verificar se retornou vazio
                    if response_data.strip() in ["Retorno sem dados!", "Sem dados", "[]", ""]:
                        print("[INFO] Dashboard: API de estatísticas retornou sem dados")
                        return {'erros_hoje': 0}
                    
                    # Parse JSON
                    data = json.loads(response_data)
                    
                    print(f"[DEBUG] Logs: Endpoint otimizado funcionou!")
                    print(f"[DEBUG] Logs: Tipo da resposta: {type(data)}")
                    print(f"[DEBUG] Logs: Conteúdo da resposta: {data}")
                    
                    # Validar estrutura da resposta
                    if isinstance(data, dict):
                        # Verificar se tem os campos esperados: 'erros', 'total', 'warnings'
                        if 'erros' in data or 'total' in data:
                            total_erros = data.get('erros', 0)
                            
                            print(f"[DEBUG] Logs: {total_erros} erros hoje (contagem precisa via COUNT)")
                            
                            return {
                                'erros_hoje': total_erros,
                                'total_logs': data.get('total', 0),
                                'total_warnings': data.get('warnings', 0)
                            }
                        else:
                            print(f"[WARNING] Logs: Resposta do endpoint otimizado inválida - Keys: {list(data.keys())}")
                            # Continua para fallback
                            raise Exception("Resposta inválida do endpoint otimizado")
                    else:
                        print(f"[WARNING] Logs: Resposta não é um dicionário")
                        raise Exception("Resposta inválida do endpoint otimizado")
                        
            except urllib.error.HTTPError as http_err:
                if http_err.code == 404:
                    print(f"[INFO] Endpoint otimizado não disponível (404) - Usando fallback...")
                    # Continua para fallback
                else:
                    print(f"[WARNING] Erro HTTP no endpoint otimizado: {http_err.code}")
                    raise  # Re-lança para tratamento externo
            
            # ========================================
            # PASSO 2: FALLBACK - Endpoint antigo
            # ========================================
            print(f"[DEBUG] Logs: Usando endpoint FALLBACK (antigo)")
            
            url = f"https://{base_url}/api/consulta/log/filtros"
            params = urllib.parse.urlencode({
                'token': token,
                'data_inicio': hoje
            })
            full_url = f"{url}?{params}"
            
            print(f"[DEBUG] Logs URL fallback: {url}")
            print(f"[DEBUG] Logs URL fallback: {url}")
            print(f"[DEBUG] Logs: Fazendo requisição fallback...")
            
            req = urllib.request.Request(full_url)
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read().decode('utf-8')
                
                # Verificar se a resposta é "Retorno sem dados!" ou similar
                if response_data.strip() in ["Retorno sem dados!", "Sem dados", "[]", ""]:
                    print("[INFO] Dashboard: API de logs (fallback) retornou sem dados")
                    return {'erros_hoje': 0}
                
                # Tentar fazer parse do JSON
                try:
                    data = json.loads(response_data)
                except json.JSONDecodeError as json_err:
                    print(f"[ERROR] Dashboard: Resposta da API de logs não é JSON válido: {response_data[:200]}")
                    print(f"[ERROR] Dashboard: JSONDecodeError: {json_err}")
                    return {'erros_hoje': 0}
                
                print(f"[DEBUG] Logs (fallback): Resposta recebida")
                print(f"[DEBUG] Logs (fallback): Tipo da resposta: {type(data)}")
                
                # A API pode retornar uma lista diretamente ou um dicionário
                if isinstance(data, list):
                    print(f"[DEBUG] Logs (fallback): API retornou lista direta com {len(data)} itens")
                    logs = data
                elif isinstance(data, dict):
                    print(f"[DEBUG] Logs (fallback): API retornou dicionário")
                    print(f"[DEBUG] Logs (fallback): Keys: {list(data.keys())}")
                    
                    if data.get('sucesso'):
                        logs = data.get('logs', [])
                        print(f"[DEBUG] Logs (fallback): Extraídos {len(logs)} logs do campo 'logs'")
                    else:
                        print(f"[DEBUG] Logs (fallback): sucesso=False")
                        return {'erros_hoje': 0}
                else:
                    print(f"[DEBUG] Logs (fallback): Tipo inesperado da resposta")
                    return {'erros_hoje': 0}
                
                # ⚠️ ATENÇÃO: Contagem de erros pode estar INCOMPLETA
                # Este método conta apenas erros nos logs retornados (máximo ~100)
                # Se houver mais logs no dia, erros antigos não serão contados
                erros_hoje = sum(1 for log in logs if log.get('tipo') == 'E')
                print(f"[WARNING] Logs (fallback): {erros_hoje} erros nos últimos {len(logs)} logs (⚠️ PODE ESTAR INCOMPLETO!)")
                
                return {'erros_hoje': erros_hoje}
                
        except urllib.error.HTTPError as http_err:
            # 404 = API de logs não disponível (normal para alguns clientes como OKVENDAS)
            if http_err.code == 404:
                print(f"[INFO] API de logs não disponível para este cliente (404) - Dashboard funcionará sem estatísticas de logs")
                return {'erros_hoje': 0}
            else:
                print(f"[WARNING] Erro HTTP ao buscar logs: {http_err.code} - {http_err.reason}")
                return {'erros_hoje': 0}
        except urllib.error.URLError as url_err:
            print(f"[WARNING] Erro de conexão ao buscar logs: {url_err.reason}")
            return {'erros_hoje': 0}
        except Exception as e:
            print(f"[WARNING] Erro inesperado ao buscar stats de logs: {e}")
            # Não mostra traceback completo para não poluir os logs
        
        return {'erros_hoje': 0}
    
    def _get_recent_executions(self):
        """Busca jobs com suas últimas execuções e intervalos"""
        try:
            if not self.token_manager:
                return []
            
            # Obtém URL base
            base_url = self.token_manager.get_base_url()
            if not base_url:
                return []
            
            active_token = self.token_manager.get_active_token()
            if not active_token:
                return []
            
            import urllib.request
            import urllib.parse
            import json
            from datetime import datetime
            
            token = active_token.get('token', '')
            url = f"https://{base_url}/api/consulta/oking_hub/filtros"
            params = urllib.parse.urlencode({'token': token})
            full_url = f"{url}?{params}"
            
            req = urllib.request.Request(full_url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if isinstance(data, dict) and 'modulos' in data:
                    jobs = data.get('modulos', [])
                    
                    # Ordenar por última execução (mais recente primeiro)
                    jobs_com_execucao = []
                    for job in jobs:
                        ultima_exec_str = job.get('ultima_execucao')
                        if ultima_exec_str:
                            try:
                                # Tentar parsear a data
                                if '.' in ultima_exec_str:
                                    # Remover microsegundos se existir
                                    ultima_exec_str = ultima_exec_str.split('.')[0]
                                
                                ultima_exec = datetime.strptime(ultima_exec_str, '%Y-%m-%d %H:%M:%S')
                                
                                jobs_com_execucao.append({
                                    'nome_job': job.get('nome_job', 'Job desconhecido'),
                                    'job': job.get('job', ''),
                                    'ultima_execucao': ultima_exec,
                                    'ultima_execucao_str': ultima_exec.strftime('%d/%m %H:%M'),
                                    'tempo_execucao': job.get('tempo_execucao', 0),
                                    'ativo': job.get('ativo') == 'S'
                                })
                            except Exception as e:
                                print(f"[DEBUG] Erro ao parsear data do job {job.get('job')}: {e}")
                                continue
                    
                    # Ordenar por data mais recente
                    jobs_com_execucao.sort(key=lambda x: x['ultima_execucao'], reverse=True)
                    
                    return jobs_com_execucao[:5]  # Retorna os 5 mais recentes
                    
        except Exception as e:
            print(f"[ERROR] Erro ao buscar execuções recentes: {e}")
            import traceback
            traceback.print_exc()
        
        return []
    
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
    
    def _go_to_errors(self):
        """Navega para a tela de Logs com filtro de erros de hoje"""
        # Mudar para a aba de logs
        self._switch_tab("logs")
        
        # Aguardar um pouco para a tela ser renderizada
        self.root.after(100, lambda: self._apply_error_filters())
    
    def _apply_error_filters(self):
        """Aplica filtros de erro na tela de logs"""
        logs_screen = self.screen_instances.get("logs")
        if logs_screen and hasattr(logs_screen, 'set_filters'):
            # Definir filtros: Status = Erro, Período = Hoje
            logs_screen.set_filters(status="Erro", date="Hoje")
    
    def _go_to_logs_filtered(self, job_name):
        """Navega para a tela de Logs com filtro específico do job"""
        # Mudar para a aba de logs
        self._switch_tab("logs")
        
        # Aguardar um pouco para a tela ser renderizada
        self.root.after(100, lambda: self._apply_job_log_filters(job_name))
    
    def _apply_job_log_filters(self, job_name):
        """Aplica filtros de job específico na tela de logs"""
        logs_screen = self.screen_instances.get("logs")
        if logs_screen and hasattr(logs_screen, 'set_filters'):
            # Definir filtros: Job = job_name, Período = Todos
            logs_screen.set_filters(job=job_name, date="Todos")
    
    def _create_tooltip(self, widget, text):
        """Cria tooltip para um widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                background="#1e293b",
                foreground="white",
                relief="solid",
                borderwidth=1,
                font=self.theme.get_font("xs"),
                padx=8,
                pady=4
            )
            label.pack()
            
            # Guardar referência do tooltip no widget
            widget._tooltip = tooltip
            
            # Remover tooltip após 3 segundos
            widget.after(3000, lambda: tooltip.destroy() if tooltip.winfo_exists() else None)
        
        def hide_tooltip(event):
            if hasattr(widget, '_tooltip') and widget._tooltip.winfo_exists():
                widget._tooltip.destroy()
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def _on_token_changed(self, token_data):
        """
        Callback chamado quando o token ativo é alterado.
        Recarrega todo o sistema com o novo token.
        
        Args:
            token_data: Dados do novo token ativo
        """
        try:
            print("\n" + "="*80)
            print("🔄 [RELOAD] Iniciando troca de token...")
            print("="*80)
            
            # Atualizar informações do token
            self.shortname = self.token_manager.get_shortname()
            active_token = self.token_manager.get_active_token()
            
            print(f"📦 [RELOAD] Shortname: {self.shortname}")
            print(f"🔑 [RELOAD] Token ativo: {active_token['nome'] if active_token else 'None'}")
            
            if not active_token:
                messagebox.showerror("Erro", "Não foi possível obter informações do token ativo")
                return
            
            # Atualizar variáveis globais (compatibilidade)
            import src
            src.shortname_interface = self.shortname
            src.token_interface = active_token['token']
            src.nome_token = active_token['nome']
            
            print(f"✅ [RELOAD] Variáveis globais atualizadas")
            
            # Mostrar tela de carregamento
            self._show_loading_overlay("🔄 Recarregando sistema com novo token...")
            
            # Agendar reload após pequeno delay (para UI atualizar)
            self.root.after(500, self._reload_system_data)
            
        except Exception as e:
            print(f"❌ [RELOAD] ERRO ao trocar token: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao trocar token:\n{str(e)}")
    
    def _show_loading_overlay(self, message):
        """Mostra overlay de carregamento"""
        # Criar overlay semi-transparente
        self.loading_overlay = tk.Frame(self.root, bg='#1e293b')
        self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Container central
        container = tk.Frame(self.loading_overlay, bg='white', padx=40, pady=30)
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(
            container,
            text=message,
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.PRIMARY,
            bg='white'
        ).pack(pady=10)
        
        # Barra de progresso indeterminada
        progress = ttk.Progressbar(container, mode='indeterminate', length=300)
        progress.pack(pady=10)
        progress.start(10)
        
        self.root.update()
    
    def _hide_loading_overlay(self):
        """Esconde overlay de carregamento"""
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.destroy()
            del self.loading_overlay
    
    def _reload_system_data(self):
        """Recarrega dados do sistema (jobs, header, dashboard)"""
        try:
            print("\n" + "="*80)
            print("🔄 [RELOAD] Recarregando dados do sistema...")
            print("="*80)
            
            from src.api import oking
            
            # 1. Recarregar jobs da API
            print(f"📡 [RELOAD] Buscando jobs da API...")
            print(f"    Shortname: {self.shortname}")
            
            active_token = self.token_manager.get_active_token()
            print(f"    Token: {active_token['nome']}")
            print(f"    Token (primeiros 20 chars): {active_token['token'][:20]}...")
            
            try:
                filtros_response = oking.get_filtros(self.shortname, active_token['token'])
                
                print(f"📥 [RELOAD] Resposta da API recebida")
                print(f"    Response: {filtros_response}")
                print(f"    Has data: {filtros_response and filtros_response.data}")
                
                if filtros_response and filtros_response.data:
                    jobs_config = filtros_response.data
                    
                    print(f"📋 [RELOAD] Jobs config keys: {jobs_config.keys() if isinstance(jobs_config, dict) else 'N/A'}")
                    
                    # Formatar jobs
                    jobs_antigos = len(self.jobs_data)
                    self.jobs_data = []
                    
                    if 'jobs' in jobs_config:
                        print(f"✅ [RELOAD] Encontrado {len(jobs_config['jobs'])} jobs na configuração")
                        
                        for idx, job in enumerate(jobs_config['jobs']):
                            job_formatted = {
                                'name': job.get('job_name', 'Job Desconhecido'),
                                'status': 'ativo' if job.get('ativo') == 'S' else 'inativo',
                                'last_run': job.get('ultima_execucao', 'Nunca'),
                                'interval': f"{job.get('intervalo', '?')} min"
                            }
                            self.jobs_data.append(job_formatted)
                            print(f"    Job {idx+1}: {job_formatted['name']} ({job_formatted['status']})")
                    else:
                        print(f"⚠️ [RELOAD] Chave 'jobs' não encontrada na resposta")
                    
                    print(f"📊 [RELOAD] Jobs antes: {jobs_antigos}, Jobs agora: {len(self.jobs_data)}")
                else:
                    print(f"⚠️ [RELOAD] Resposta da API vazia ou sem dados")
                    self.jobs_data = []
            except Exception as e:
                print(f"❌ [RELOAD] ERRO ao recarregar jobs: {e}")
                import traceback
                traceback.print_exc()
                self.jobs_data = []
            
            # 2. Atualizar header
            print(f"🔄 [RELOAD] Atualizando header...")
            self._update_header()
            
            # 3. Recarregar SIDEBAR (menu de jobs)
            print(f"🔄 [RELOAD] Reconstruindo sidebar...")
            self._rebuild_sidebar()
            
            # 4. Recarregar tela atual (se for overview ou jobs)
            print(f"🔄 [RELOAD] Tela atual: {self.current_tab}")
            if self.current_tab == 'overview':
                print(f"    Recarregando Overview...")
                self._switch_tab('overview')
            elif self.current_tab == 'jobs':
                print(f"    Recarregando Jobs...")
                self._switch_tab('jobs')
            
            # 5. Limpar cache de telas antigas
            print(f"🗑️ [RELOAD] Limpando cache de {len(self.screen_instances)} telas...")
            self.screen_instances.clear()
            
            # Esconder loading
            self._hide_loading_overlay()
            
            print("\n" + "="*80)
            print(f"✅ [RELOAD] Reload completo!")
            print(f"    Token: {active_token['nome']}")
            print(f"    Jobs: {len(self.jobs_data)}")
            print("="*80 + "\n")
            
            # Mensagem de sucesso
            messagebox.showinfo(
                "Sucesso",
                f"✅ Sistema recarregado com sucesso!\n\n"
                f"Token ativo: {active_token['nome']}\n"
                f"Jobs carregados: {len(self.jobs_data)}",
                parent=self.root
            )
            
        except Exception as e:
            print(f"\n❌ [RELOAD] ERRO CRÍTICO: {e}")
            import traceback
            traceback.print_exc()
            self._hide_loading_overlay()
            messagebox.showerror("Erro", f"Erro ao recarregar sistema:\n{str(e)}")
    
    def _rebuild_sidebar(self):
        """Reconstrói menu de jobs na sidebar"""
        try:
            print(f"🔧 [REBUILD] Chamando _load_jobs_submenu()...")
            self._load_jobs_submenu()
            print(f"✅ [REBUILD] Sidebar reconstruída com sucesso")
        except Exception as e:
            print(f"❌ [REBUILD] Erro ao reconstruir sidebar: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_header(self):
        """Atualiza informações do header"""
        try:
            # Atualizar label do token ativo no header
            active_token = self.token_manager.get_active_token()
            if active_token and hasattr(self, 'token_label'):
                self.token_label.config(text=f"🔑 {active_token['nome']}")
        except:
            pass
    
    def _confirm_exit(self):
        """Confirma saída do sistema"""
        if messagebox.askyesno("Confirmar Saída", "Deseja realmente sair do OKING Hub?"):
            self.root.quit()


# ==================== EXECUÇÃO ====================

if __name__ == "__main__":
    root = tk.Tk()
    app = IntegratedDashboard(root)
    root.mainloop()
