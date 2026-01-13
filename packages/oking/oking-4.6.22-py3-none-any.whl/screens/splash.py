"""
Splash Screen - Tela de carregamento inicial
"""

import tkinter as tk
from ui_components import ModernTheme


class SplashScreen:
    """Tela de carregamento com logo e progresso"""
    
    def __init__(self, parent=None):
        """
        Args:
            parent: Janela pai (opcional)
        """
        self.theme = ModernTheme()
        
        # Cria janela
        if parent:
            self.splash = tk.Toplevel(parent)
        else:
            self.splash = tk.Tk()
        
        self.splash.title("OKING HUB")
        self.splash.geometry("500x400")
        self.splash.configure(bg=self.theme.BG_PRIMARY)
        self.splash.overrideredirect(True)  # Remove bordas
        
        # Centraliza
        self.splash.update_idletasks()
        x = (self.splash.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.splash.winfo_screenheight() // 2) - (400 // 2)
        self.splash.geometry(f"500x400+{x}+{y}")
        
        self._build_ui()
    
    def _build_ui(self):
        """Constrói interface"""
        # Container principal
        container = tk.Frame(self.splash, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Logo (placeholder - substitua por imagem real)
        logo_frame = tk.Frame(container, bg=self.theme.PRIMARY, width=120, height=120)
        logo_frame.pack(pady=(40, 20))
        logo_frame.pack_propagate(False)
        
        logo_text = tk.Label(
            logo_frame,
            text="OKING",
            font=('Segoe UI', 28, 'bold'),
            bg=self.theme.PRIMARY,
            fg='white'
        )
        logo_text.place(relx=0.5, rely=0.5, anchor='center')
        
        # Título
        title = tk.Label(
            container,
            text="OKING HUB",
            font=('Segoe UI', 24, 'bold'),
            bg=self.theme.BG_PRIMARY,
            fg=self.theme.TEXT_PRIMARY
        )
        title.pack(pady=(0, 8))
        
        # Subtítulo
        subtitle = tk.Label(
            container,
            text="Facilitando Integrações",
            font=self.theme.get_font("md"),
            bg=self.theme.BG_PRIMARY,
            fg=self.theme.TEXT_SECONDARY
        )
        subtitle.pack(pady=(0, 40))
        
        # Barra de progresso
        progress_frame = tk.Frame(container, bg=self.theme.BG_SECONDARY, height=6)
        progress_frame.pack(fill='x', pady=(0, 16))
        
        self.progress_bar = tk.Frame(progress_frame, bg=self.theme.PRIMARY, height=6)
        self.progress_bar.place(x=0, y=0, relwidth=0, relheight=1)
        
        # Status
        self.status_label = tk.Label(
            container,
            text="Iniciando...",
            font=self.theme.get_font("sm"),
            bg=self.theme.BG_PRIMARY,
            fg=self.theme.TEXT_SECONDARY
        )
        self.status_label.pack()
        
        # Versão
        version_label = tk.Label(
            container,
            text="v4.5.22",
            font=('Segoe UI', 9),
            bg=self.theme.BG_PRIMARY,
            fg=self.theme.TEXT_TERTIARY
        )
        version_label.pack(side='bottom')
    
    def update_progress(self, progress: float, status: str = None):
        """
        Atualiza progresso
        
        Args:
            progress: Progresso de 0 a 1
            status: Texto de status (opcional)
        """
        self.progress_bar.place(relwidth=progress)
        
        if status:
            self.status_label.config(text=status)
        
        self.splash.update()
    
    def close(self):
        """Fecha o splash"""
        self.splash.destroy()
    
    def show(self):
        """Exibe o splash"""
        self.splash.deiconify()
