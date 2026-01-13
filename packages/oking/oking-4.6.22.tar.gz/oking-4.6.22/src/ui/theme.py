"""
Sistema de temas modernos para OKING Hub
Substitui PySimpleGUI por Tkinter puro com design moderno
"""


class ModernTheme:
    """Tema moderno para a interface OKING Hub"""
    
    # Cores principais
    PRIMARY = "#2563eb"          # Azul vibrante
    PRIMARY_DARK = "#1e40af"     # Azul escuro
    PRIMARY_LIGHT = "#3b82f6"    # Azul claro
    
    # Cores de fundo
    BG_PRIMARY = "#ffffff"       # Branco
    BG_SECONDARY = "#f8fafc"     # Cinza muito claro
    BG_TERTIARY = "#f1f5f9"      # Cinza claro
    
    # Cores de texto
    TEXT_PRIMARY = "#0f172a"     # Preto suave
    TEXT_SECONDARY = "#64748b"   # Cinza médio
    TEXT_TERTIARY = "#94a3b8"    # Cinza claro
    
    # Cores de status
    SUCCESS = "#10b981"          # Verde
    SUCCESS_BG = "#d1fae5"       # Verde claro
    WARNING = "#f59e0b"          # Laranja
    WARNING_BG = "#fef3c7"       # Laranja claro
    DANGER = "#ef4444"           # Vermelho
    DANGER_BG = "#fee2e2"        # Vermelho claro
    INFO = "#3b82f6"             # Azul
    INFO_BG = "#dbeafe"          # Azul claro
    
    # Cores neutras
    BORDER = "#e2e8f0"           # Borda padrão
    BORDER_LIGHT = "#f1f5f9"     # Borda clara
    SHADOW = "#00000010"         # Sombra leve
    
    # Tipografia
    FONT_FAMILY = "Segoe UI"     # Fonte moderna (Windows)
    FONT_FAMILY_MAC = "SF Pro Display"  # Fonte macOS
    FONT_FAMILY_LINUX = "Ubuntu"        # Fonte Linux
    
    FONT_SIZE_XL = 24
    FONT_SIZE_LG = 18
    FONT_SIZE_MD = 14
    FONT_SIZE_SM = 12
    FONT_SIZE_XS = 10
    
    # Espaçamentos
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    SPACING_XL = 32
    
    # Bordas e raios
    BORDER_RADIUS = 8
    BORDER_RADIUS_SM = 4
    BORDER_RADIUS_LG = 12
    
    # Sombras
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
    
    @classmethod
    def get_font(cls, size="md", weight="normal"):
        """Retorna configuração de fonte"""
        sizes = {
            "xs": cls.FONT_SIZE_XS,
            "sm": cls.FONT_SIZE_SM,
            "md": cls.FONT_SIZE_MD,
            "lg": cls.FONT_SIZE_LG,
            "xl": cls.FONT_SIZE_XL
        }
        
        weights = {
            "normal": "normal",
            "bold": "bold"
        }
        
        return (cls.FONT_FAMILY, sizes.get(size, cls.FONT_SIZE_MD), weights.get(weight, "normal"))


class DarkTheme(ModernTheme):
    """Tema escuro para a interface OKING Hub"""
    
    # Cores principais (mantém as mesmas)
    PRIMARY = "#3b82f6"
    PRIMARY_DARK = "#2563eb"
    PRIMARY_LIGHT = "#60a5fa"
    
    # Cores de fundo (invertidas)
    BG_PRIMARY = "#0f172a"       # Azul escuro profundo
    BG_SECONDARY = "#1e293b"     # Azul escuro médio
    BG_TERTIARY = "#334155"      # Azul escuro claro
    
    # Cores de texto (invertidas)
    TEXT_PRIMARY = "#f8fafc"     # Branco suave
    TEXT_SECONDARY = "#cbd5e1"   # Cinza claro
    TEXT_TERTIARY = "#94a3b8"    # Cinza médio
    
    # Cores de status (ajustadas para dark)
    SUCCESS = "#22c55e"
    SUCCESS_BG = "#14532d"
    WARNING = "#fbbf24"
    WARNING_BG = "#78350f"
    DANGER = "#f87171"
    DANGER_BG = "#7f1d1d"
    INFO = "#60a5fa"
    INFO_BG = "#1e3a8a"
    
    # Cores neutras
    BORDER = "#334155"
    BORDER_LIGHT = "#475569"
    SHADOW = "#00000040"
