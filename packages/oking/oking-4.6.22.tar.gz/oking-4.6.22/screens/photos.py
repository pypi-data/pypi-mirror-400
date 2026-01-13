"""
📸 Tela de Upload de Fotos - OKING Hub
Interface moderna para upload de fotos com preview (Pillow opcional)
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from datetime import datetime
from ui_components import ModernTheme, Card, ModernButton, StatusBadge

# Tentar importar Pillow (opcional)
try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


# ==================== COMPONENTES ====================

class DropZone(tk.Frame):
    """Área de arrastar e soltar fotos"""
    def __init__(self, parent, theme=None, on_drop=None, **kwargs):
        self.theme = theme or ModernTheme()
        self.on_drop = on_drop
        
        super().__init__(
            parent,
            bg=self.theme.BG_TERTIARY,
            relief='flat',
            borderwidth=2,
            highlightthickness=2,
            highlightbackground=self.theme.BORDER,
            **kwargs
        )
        
        # Conteúdo
        container = tk.Frame(self, bg=self.theme.BG_TERTIARY)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        tk.Label(
            container,
            text="📁",
            font=("Segoe UI", 48),
            fg=self.theme.TEXT_TERTIARY,
            bg=self.theme.BG_TERTIARY
        ).pack()
        
        tk.Label(
            container,
            text="Arraste fotos aqui ou clique para selecionar",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_TERTIARY
        ).pack(pady=(16, 8))
        
        tk.Label(
            container,
            text="Formatos aceitos: JPG, PNG, GIF • Tamanho máximo: 10MB",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_TERTIARY
        ).pack()
        
        # Botão de seleção
        ModernButton(
            container,
            text="📂 Selecionar Arquivos",
            variant="primary",
            theme=self.theme,
            command=self._select_files
        ).pack(pady=(20, 0))
        
        # Bind de click
        self.configure(cursor='hand2')
        self.bind('<Button-1>', lambda e: self._select_files())
        for widget in self.winfo_children():
            widget.bind('<Button-1>', lambda e: self._select_files())
            for child in widget.winfo_children():
                child.bind('<Button-1>', lambda e: self._select_files())
    
    def _select_files(self):
        """Abre diálogo de seleção de arquivos"""
        files = filedialog.askopenfilenames(
            title="Selecionar Fotos",
            filetypes=[
                ("Imagens", "*.jpg *.jpeg *.png *.gif"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if files and self.on_drop:
            self.on_drop(files)


class PhotoCard(tk.Frame):
    """Card de foto individual"""
    def __init__(self, parent, photo_data, theme=None, on_remove=None, on_upload=None):
        self.theme = theme or ModernTheme()
        self.photo_data = photo_data
        self.on_remove = on_remove
        self.on_upload = on_upload
        
        super().__init__(
            parent,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.BORDER
        )
        
        self._build_ui()
    
    def _build_ui(self):
        container = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=16, pady=16)
        
        # Grid layout
        # Coluna 1: Preview (se Pillow disponível)
        if PILLOW_AVAILABLE:
            preview_frame = tk.Frame(container, bg=self.theme.BG_TERTIARY, width=100, height=100)
            preview_frame.pack(side='left', padx=(0, 16))
            preview_frame.pack_propagate(False)
            
            try:
                img = Image.open(self.photo_data['path'])
                img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                label = tk.Label(preview_frame, image=photo, bg=self.theme.BG_TERTIARY)
                label.image = photo  # Manter referência
                label.pack(expand=True)
            except:
                tk.Label(
                    preview_frame,
                    text="📷",
                    font=("Segoe UI", 32),
                    fg=self.theme.TEXT_TERTIARY,
                    bg=self.theme.BG_TERTIARY
                ).pack(expand=True)
        else:
            # Ícone sem preview
            icon_frame = tk.Frame(container, bg=self.theme.BG_TERTIARY, width=100, height=100)
            icon_frame.pack(side='left', padx=(0, 16))
            icon_frame.pack_propagate(False)
            
            tk.Label(
                icon_frame,
                text="📷",
                font=("Segoe UI", 32),
                fg=self.theme.TEXT_TERTIARY,
                bg=self.theme.BG_TERTIARY
            ).pack(expand=True)
        
        # Coluna 2: Informações
        info = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        info.pack(side='left', fill='both', expand=True)
        
        # Nome do arquivo
        tk.Label(
            info,
            text=os.path.basename(self.photo_data['path']),
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x')
        
        # Tamanho
        size_mb = self.photo_data.get('size', 0) / (1024 * 1024)
        tk.Label(
            info,
            text=f"📊 Tamanho: {size_mb:.2f} MB",
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x', pady=(4, 0))
        
        # Status
        status_map = {
            'pending': ('⏳ Pendente', 'pending'),
            'uploading': ('⏫ Enviando...', 'info'),
            'success': ('✓ Enviado', 'success'),
            'error': ('✗ Erro', 'error')
        }
        status_text, status_type = status_map.get(
            self.photo_data.get('status', 'pending'),
            ('⏳ Pendente', 'pending')
        )
        
        StatusBadge(
            info,
            text=status_text,
            status=status_type,
            theme=self.theme
        ).pack(anchor='w', pady=(8, 0))
        
        # Coluna 3: Botões
        buttons = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        buttons.pack(side='right', padx=(16, 0))
        
        if self.photo_data.get('status') == 'pending':
            ModernButton(
                buttons,
                text="📤 Enviar",
                variant="success",
                theme=self.theme,
                command=lambda: self.on_upload and self.on_upload(self.photo_data)
            ).pack(pady=(0, 8))
        
        ModernButton(
            buttons,
            text="🗑️ Remover",
            variant="danger",
            theme=self.theme,
            command=lambda: self.on_remove and self.on_remove(self.photo_data)
        ).pack()


# ==================== TELA PRINCIPAL ====================

class PhotosScreen(tk.Frame):
    """Tela de upload de fotos"""
    
    def __init__(self, parent, theme=None):
        self.theme = theme if theme else ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY)
        self.photos = []
        self.canvas = None  # Referência ao canvas
        
        self._build_ui()
        
        # ✅ Limpeza ao destruir
        self.bind("<Destroy>", self._on_destroy)
        
        # Aviso se Pillow não estiver disponível
        if not PILLOW_AVAILABLE:
            self.after(500, self._show_pillow_warning)
    
    def _on_destroy(self, event):
        """Limpa bindings ao destruir"""
        if event.widget == self:
            try:
                self.unbind_all("<MouseWheel>")
            except:
                pass
    
    def _show_pillow_warning(self):
        """Avisa que Pillow não está instalado"""
        messagebox.showinfo(
            "Preview Desabilitado",
            "📸 Pillow não está instalado.\n\n"
            "A tela funcionará, mas sem preview de imagens.\n\n"
            "Para habilitar preview, instale:\n"
            "pip install Pillow",
            parent=self.winfo_toplevel()
        )
    
    def _build_ui(self):
        """Constrói interface"""
        # Container principal
        main_container = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        main_container.pack(fill='both', expand=True, padx=24, pady=24)
        
        # Header
        self._build_header(main_container)
        
        # Canvas com scroll
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
        
        # ✅ MouseWheel - Vinculado apenas quando mouse sobre canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Salvar referência
        self.canvas = canvas
        
        canvas.pack(side="left", fill="both", expand=True, pady=(16, 0))
        scrollbar.pack(side="right", fill="y", pady=(16, 0))
        
        # Stats
        self.stats_container = tk.Frame(self.scrollable_frame, bg=self.theme.BG_SECONDARY)
        self.stats_container.pack(fill='x', pady=(0, 16))
        self._build_stats()
        
        # Upload zone
        self._build_upload_zone()
        
        # Photos list
        self.photos_container = tk.Frame(self.scrollable_frame, bg=self.theme.BG_SECONDARY)
        self.photos_container.pack(fill='both', expand=True)
    
    def _build_header(self, parent):
        """Header da tela"""
        card = Card(parent, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        # Lado esquerdo
        left = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        left.pack(side='left')
        
        tk.Label(
            left,
            text="📸 Upload de Fotos",
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        pillow_status = "✅ Preview habilitado" if PILLOW_AVAILABLE else "⚠️ Preview desabilitado"
        pillow_color = self.theme.SUCCESS if PILLOW_AVAILABLE else self.theme.WARNING
        
        tk.Label(
            left,
            text=f"  •  {pillow_status}",
            font=self.theme.get_font("sm"),
            fg=pillow_color,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        # Lado direito
        ModernButton(
            container,
            text="📤 Enviar Todas",
            variant="success",
            theme=self.theme,
            command=self._upload_all
        ).pack(side='right')
    
    def _build_stats(self):
        """Estatísticas"""
        # Limpa stats
        for widget in self.stats_container.winfo_children():
            widget.destroy()
        
        card = Card(self.stats_container, theme=self.theme)
        card.pack(fill='x')
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        # Total
        self._create_stat_box(
            container,
            "📁 Total",
            str(len(self.photos)),
            self.theme.INFO
        ).pack(side='left', padx=(0, 16))
        
        # Enviadas
        uploaded = len([p for p in self.photos if p.get('status') == 'success'])
        self._create_stat_box(
            container,
            "✓ Enviadas",
            str(uploaded),
            self.theme.SUCCESS
        ).pack(side='left', padx=(0, 16))
        
        # Pendentes
        pending = len([p for p in self.photos if p.get('status') == 'pending'])
        self._create_stat_box(
            container,
            "⏳ Pendentes",
            str(pending),
            self.theme.WARNING
        ).pack(side='left', padx=(0, 16))
        
        # Erros
        errors = len([p for p in self.photos if p.get('status') == 'error'])
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
    
    def _build_upload_zone(self):
        """Zona de upload"""
        card = Card(self.scrollable_frame, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            container,
            text="📤 Adicionar Fotos",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 16))
        
        DropZone(
            container,
            theme=self.theme,
            on_drop=self._handle_files
        ).pack(fill='x')
    
    def _handle_files(self, files):
        """Processa arquivos selecionados"""
        for file_path in files:
            # Validação
            if not os.path.exists(file_path):
                continue
            
            size = os.path.getsize(file_path)
            
            # Limite de 10MB
            if size > 10 * 1024 * 1024:
                messagebox.showwarning(
                    "Arquivo muito grande",
                    f"{os.path.basename(file_path)}\n\nTamanho máximo: 10MB",
                    parent=self.winfo_toplevel()
                )
                continue
            
            # Adiciona à lista
            photo_data = {
                'id': len(self.photos),
                'path': file_path,
                'size': size,
                'status': 'pending',
                'added_at': datetime.now().isoformat()
            }
            
            self.photos.append(photo_data)
        
        self._refresh_photos_list()
        self._build_stats()
    
    def _refresh_photos_list(self):
        """Atualiza lista de fotos"""
        # Limpa lista
        for widget in self.photos_container.winfo_children():
            widget.destroy()
        
        if not self.photos:
            self._show_empty_state()
            return
        
        # Card da lista
        card = Card(self.photos_container, theme=self.theme)
        card.pack(fill='both', expand=True)
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(
            container,
            text=f"📋 Fotos na Fila ({len(self.photos)})",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 16))
        
        # Fotos
        for photo in self.photos:
            PhotoCard(
                container,
                photo,
                theme=self.theme,
                on_remove=self._remove_photo,
                on_upload=self._upload_photo
            ).pack(fill='x', pady=(0, 12))
    
    def _show_empty_state(self):
        """Mostra estado vazio"""
        card = Card(self.photos_container, theme=self.theme)
        card.pack(fill='x')
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=40, pady=60)
        
        tk.Label(
            container,
            text="📁 Nenhuma foto adicionada",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack()
        
        tk.Label(
            container,
            text="Use a área acima para adicionar fotos",
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_TERTIARY,
            bg=self.theme.BG_PRIMARY
        ).pack(pady=(8, 0))
    
    def _upload_photo(self, photo_data):
        """Envia uma foto"""
        photo_data['status'] = 'uploading'
        self._refresh_photos_list()
        self._build_stats()
        
        # Simula upload
        self.after(1500, lambda: self._finish_upload(photo_data))
    
    def _finish_upload(self, photo_data):
        """Finaliza upload"""
        photo_data['status'] = 'success'
        photo_data['uploaded_at'] = datetime.now().isoformat()
        self._refresh_photos_list()
        self._build_stats()
    
    def _upload_all(self):
        """Envia todas as fotos pendentes"""
        pending = [p for p in self.photos if p.get('status') == 'pending']
        
        if not pending:
            messagebox.showinfo(
                "Nenhuma foto pendente",
                "Todas as fotos já foram enviadas!",
                parent=self.winfo_toplevel()
            )
            return
        
        for photo in pending:
            self._upload_photo(photo)
    
    def _remove_photo(self, photo_data):
        """Remove foto da lista"""
        self.photos = [p for p in self.photos if p.get('id') != photo_data.get('id')]
        self._refresh_photos_list()
        self._build_stats()
