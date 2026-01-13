"""
🎨 Tela de Configurações - OKING Hub (Versão Integrada)
Gerenciamento de tema e aparência
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
from pathlib import Path
from datetime import datetime
from ui_components import ModernTheme, Card, ModernButton, ScrollableFrame


# ==================== STORAGE ====================

class SettingsStorage:
    """Armazenamento de configurações"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.oking'
        self.config_file = self.config_dir / 'settings.json'
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_settings(self):
        """Carrega configurações"""
        try:
            if not self.config_file.exists():
                return self._get_default_settings()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self._get_default_settings()
    
    def save_settings(self, settings):
        """Salva configurações"""
        try:
            settings['updated_at'] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False
    
    def _get_default_settings(self):
        """Configurações padrão"""
        return {
            'appearance': {
                'theme': 'light',
                'primary_color': '#2563eb',
                'font_size': 12,
                'compact_mode': False
            }
        }


# ==================== COMPONENTE DE ROW ====================

class SettingRow(tk.Frame):
    """Linha de configuração"""
    def __init__(self, parent, title, description, theme=None):
        self.theme = theme or ModernTheme()
        super().__init__(parent, bg=self.theme.BG_PRIMARY)
        
        # Esquerda - textos
        left = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        left.pack(side='left', fill='both', expand=True)
        
        tk.Label(
            left,
            text=title,
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x')
        
        tk.Label(
            left,
            text=description,
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w',
            wraplength=400,
            justify='left'
        ).pack(fill='x')
        
        # Direita - controle
        self.control_container = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        self.control_container.pack(side='right', padx=(16, 0))


# ==================== TELA PRINCIPAL ====================

class SettingsScreen(tk.Frame):
    """Tela de configurações integrada"""
    
    def __init__(self, parent, dashboard=None):
        self.dashboard = dashboard  # Referência ao dashboard para aplicar mudanças
        # Usa o tema do dashboard se disponível
        self.theme = dashboard.theme if dashboard else ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY)
        
        self.storage = SettingsStorage()
        self.settings = self.storage.load_settings()
        self.vars = {}
        
        self._build_ui()
    
    def _build_ui(self):
        """Constrói interface"""
        # Scrollable frame
        scrollable = ScrollableFrame(self, theme=self.theme)
        scrollable.pack(fill='both', expand=True)
        
        self.scrollable_frame = scrollable.get_frame()
        
        # Conteúdo
        self._build_header()
        self._build_appearance_settings()
        self._build_actions()
    
    def _build_header(self):
        """Cabeçalho"""
        header = Card(self.scrollable_frame, theme=self.theme)
        header.pack(fill='x', padx=24, pady=24)
        
        container = tk.Frame(header, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        tk.Label(
            container,
            text="🎨 Tema e Aparência",
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w')
        
        tk.Label(
            container,
            text="Personalize a interface do sistema",
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(4, 0))
    
    def _build_appearance_settings(self):
        """Configurações de aparência"""
        card = Card(self.scrollable_frame, theme=self.theme)
        card.pack(fill='x', padx=24, pady=(0, 16))
        card.add_padding(20)
        
        # Título
        tk.Label(
            card,
            text="✨ Personalização",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 16))
        
        # Tema
        row = SettingRow(
            card,
            "Tema",
            "Esquema de cores da interface",
            theme=self.theme
        )
        row.pack(fill='x', pady=(0, 16))
        
        self.vars['theme'] = tk.StringVar(value=self.settings['appearance']['theme'])
        ttk.Combobox(
            row.control_container,
            textvariable=self.vars['theme'],
            values=['light', 'dark', 'auto'],
            state='readonly',
            width=12
        ).pack()
        
        # Cor primária
        row = SettingRow(
            card,
            "Cor primária",
            "Cor principal da interface",
            theme=self.theme
        )
        row.pack(fill='x', pady=(0, 16))
        
        color_frame = tk.Frame(row.control_container, bg=self.theme.BG_PRIMARY)
        color_frame.pack()
        
        self.vars['primary_color'] = tk.StringVar(value=self.settings['appearance']['primary_color'])
        
        self.color_preview = tk.Label(
            color_frame,
            text="   ",
            bg=self.vars['primary_color'].get(),
            relief='solid',
            borderwidth=1,
            width=3
        )
        self.color_preview.pack(side='left', padx=(0, 8))
        
        ModernButton(
            color_frame,
            text="Escolher Cor",
            variant="secondary",
            theme=self.theme,
            command=self._select_color,
            width=12,
            padx=12,
            pady=6
        ).pack(side='left')
        
        # Botão de preview
        ModernButton(
            color_frame,
            text="👁️ Preview",
            variant="secondary",
            theme=self.theme,
            command=self._preview_color,
            width=10,
            padx=8,
            pady=6
        ).pack(side='left', padx=(8, 0))
        
        # Tamanho da fonte
        row = SettingRow(
            card,
            "Tamanho da fonte",
            "Tamanho base do texto na interface",
            theme=self.theme
        )
        row.pack(fill='x', pady=(0, 16))
        
        self.vars['font_size'] = tk.IntVar(value=self.settings['appearance']['font_size'])
        tk.Spinbox(
            row.control_container,
            from_=10,
            to=20,
            textvariable=self.vars['font_size'],
            font=self.theme.get_font("md"),
            width=10
        ).pack()
        
    def _build_actions(self):
        """Ações"""
        card = Card(self.scrollable_frame, theme=self.theme)
        card.pack(fill='x', padx=24, pady=(0, 24))
        card.add_padding(20)
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x')
        
        # Restaurar padrões
        ModernButton(
            container,
            text="🔄 Restaurar Padrões",
            variant="secondary",
            theme=self.theme,
            command=self._restore_defaults
        ).pack(side='left')
        
        # Salvar
        ModernButton(
            container,
            text="💾 Salvar Configurações",
            variant="success",
            theme=self.theme,
            command=self._save_settings
        ).pack(side='right')
        
        # Cancelar
        ModernButton(
            container,
            text="Cancelar",
            variant="secondary",
            theme=self.theme,
            command=self._load_current_settings
        ).pack(side='right', padx=(0, 8))
    
    # ========== MÉTODOS DE AÇÃO ==========
    
    def _select_color(self):
        """Seleciona cor primária"""
        color = colorchooser.askcolor(
            title="Escolher Cor Primária",
            initialcolor=self.vars['primary_color'].get()
        )
        if color[1]:
            self.vars['primary_color'].set(color[1])
            self.color_preview.configure(bg=color[1])
    
    def _preview_color(self):
        """Preview da cor antes de salvar"""
        if not self.dashboard:
            messagebox.showinfo("Info", "Preview disponível apenas no modo integrado")
            return
        
        # Aplica temporariamente
        new_color = self.vars['primary_color'].get()
        old_color = self.theme.PRIMARY
        
        self.theme.PRIMARY = new_color
        self.theme.PRIMARY_DARK = self._darken_color(new_color)
        self.theme.PRIMARY_LIGHT = self._lighten_color(new_color)
        
        # Atualiza visual dos botões
        for tab_id, btn in self.dashboard.tab_buttons.items():
            if btn.is_active:
                btn.configure(bg=self.theme.PRIMARY)
                for widget in btn.winfo_children():
                    widget.configure(bg=self.theme.PRIMARY)
                    for child in widget.winfo_children():
                        child.configure(bg=self.theme.PRIMARY)
        
        # Mostra mensagem
        messagebox.showinfo(
            "Preview",
            "Preview aplicado!\n\n"
            "As cores dos elementos ativos foram atualizadas temporariamente.\n"
            "Clique em 'Salvar' para tornar permanente ou 'Cancelar' para reverter."
        )
    
    def _save_settings(self):
        """Salva configurações"""
        # Coleta valores
        self.settings['appearance']['theme'] = self.vars['theme'].get()
        self.settings['appearance']['primary_color'] = self.vars['primary_color'].get()
        self.settings['appearance']['font_size'] = self.vars['font_size'].get()
        
        # Salva
        if self.storage.save_settings(self.settings):
            # Aplica mudanças no tema atual
            self._apply_theme_changes()
        else:
            messagebox.showerror(
                "Erro",
                "Erro ao salvar configurações."
            )
    
    def _apply_theme_changes(self):
        """Aplica mudanças de tema em tempo real"""
        if not self.dashboard:
            return
        
        # Aplica tema (light/dark/auto)
        theme_mode = self.settings['appearance']['theme']
        
        # Por enquanto, 'auto' usa 'light'
        if theme_mode == 'auto':
            theme_mode = 'light'
        
        self.dashboard.theme.apply_mode(theme_mode)
        
        # Aplica tamanho de fonte
        font_size = self.settings['appearance']['font_size']
        self.dashboard.theme.base_font_size = font_size
        
        # Atualiza cor primária no tema
        new_color = self.settings['appearance']['primary_color']
        self.dashboard.theme.PRIMARY = new_color
        self.dashboard.theme.PRIMARY_DARK = self._darken_color(new_color)
        self.dashboard.theme.PRIMARY_LIGHT = self._lighten_color(new_color)
        
        # Força reconstrução da UI para aplicar todas as cores
        messagebox.showinfo(
            "Reiniciar Necessário",
            "Para aplicar completamente o novo tema, por favor reinicie o aplicativo."
        )
    
    def _darken_color(self, hex_color):
        """Escurece uma cor hex"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _lighten_color(self, hex_color):
        """Clareia uma cor hex"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = min(255, int(r * 1.2))
        g = min(255, int(g * 1.2))
        b = min(255, int(b * 1.2))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _load_current_settings(self):
        """Recarrega configurações atuais"""
        if messagebox.askyesno(
            "Confirmar",
            "Descartar alterações e recarregar configurações salvas?"
        ):
            self.settings = self.storage.load_settings()
            self._update_vars()
    
    def _restore_defaults(self):
        """Restaura configurações padrão"""
        if messagebox.askyesno(
            "Confirmar",
            "Restaurar TODAS as configurações para os valores padrão?\n\n"
            "Esta ação não pode ser desfeita."
        ):
            self.settings = self.storage._get_default_settings()
            self._update_vars()
            messagebox.showinfo("Sucesso", "Configurações restauradas!")
    
    def _update_vars(self):
        """Atualiza variáveis com valores atuais"""
        self.vars['theme'].set(self.settings['appearance']['theme'])
        self.vars['primary_color'].set(self.settings['appearance']['primary_color'])
        self.color_preview.configure(bg=self.settings['appearance']['primary_color'])
        self.vars['font_size'].set(self.settings['appearance']['font_size'])
