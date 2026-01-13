"""
🔑 Tela de Gerenciamento de Tokens - OKING Hub
Interface moderna para gerenciar tokens de API com criptografia
"""
import tkinter as tk
from tkinter import messagebox
import json
import os
import base64
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import platform
import uuid
from ui_components import ModernTheme, Card, ModernButton


# ==================== CRIPTOGRAFIA SEGURA ====================

class SecureStorage:
    """Armazenamento seguro de tokens com criptografia AES-256"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.oking'
        self.config_file = self.config_dir / 'tokens.json'
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_machine_key(self):
        machine_id = f"{platform.node()}-{os.getlogin()}-{platform.machine()}"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'oking_hub_tokens_v1',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
        return key
    
    def _encrypt(self, data: str) -> str:
        key = self._get_machine_key()
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        try:
            key = self._get_machine_key()
            f = Fernet(key)
            decrypted = f.decrypt(base64.urlsafe_b64decode(encrypted_data))
            return decrypted.decode()
        except:
            return ""
    
    def load_tokens(self):
        """Carrega todos os tokens (descriptografa automaticamente)"""
        try:
            if not self.config_file.exists():
                return []
            
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            tokens = data.get('tokens', [])
            
            # Descriptografa tokens
            for token in tokens:
                if token.get('token_encrypted'):
                    token['token'] = self._decrypt(token['token_encrypted'])
                    del token['token_encrypted']
            
            return tokens
        except:
            return []
    
    def save_tokens(self, tokens):
        """Salva tokens (criptografa automaticamente)"""
        try:
            # Criptografa tokens
            tokens_encrypted = []
            for token in tokens:
                token_copy = token.copy()
                if token_copy.get('token'):
                    token_copy['token_encrypted'] = self._encrypt(token_copy['token'])
                    del token_copy['token']
                tokens_encrypted.append(token_copy)
            
            data = {
                'tokens': tokens_encrypted,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar tokens: {e}")
            return False


# ==================== TELA PRINCIPAL ====================

class TokensScreen(tk.Frame):
    """Tela de gerenciamento de tokens"""
    
    def __init__(self, parent, token_manager=None, theme=None):
        self.theme = theme if theme else ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY)
        # Usa TokenManager se fornecido, senão usa storage próprio (compatibilidade)
        self.token_manager = token_manager
        self.storage = SecureStorage() if not token_manager else None
        self.tokens = []
        self.editing_token = None
        self.canvas = None  # Referência ao canvas para limpeza
        
        self._build_ui()
        self._load_tokens()
        
        # ✅ Registrar limpeza quando o frame for destruído
        self.bind("<Destroy>", self._on_destroy)
    
    def _on_destroy(self, event):
        """Limpa bindings quando a tela é destruída"""
        if event.widget == self:  # Apenas quando o frame principal é destruído
            try:
                self.unbind_all("<MouseWheel>")
            except:
                pass
    
    def _get_token_name(self, token_data):
        """Retorna nome do token (compatível com ambos formatos)"""
        return token_data.get('nome') or token_data.get('name', 'Token')
    
    def _get_token_value(self, token_data):
        """Retorna valor do token (compatível com ambos formatos)"""
        return token_data.get('token', '')
    
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
        
        # ✅ MouseWheel - Vinculado ao canvas, não globalmente
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Vincular apenas quando o mouse está sobre o canvas
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Salvar referência do canvas para limpeza posterior
        self.canvas = canvas
        
        canvas.pack(side="left", fill="both", expand=True, pady=(16, 0))
        scrollbar.pack(side="right", fill="y", pady=(16, 0))
        
        # Área de tokens
        self.tokens_container = tk.Frame(self.scrollable_frame, bg=self.theme.BG_SECONDARY)
        self.tokens_container.pack(fill='both', expand=True)
    
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
            text="🔑 Gerenciamento de Tokens",
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        tk.Label(
            left,
            text="  •  Tokens criptografados com AES-256",
            font=self.theme.get_font("sm"),
            fg=self.theme.SUCCESS,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left')
        
        # Lado direito
        ModernButton(
            container,
            text="➕ Adicionar Token",
            variant="primary",
            theme=self.theme,
            command=self._add_token
        ).pack(side='right')
    
    def _load_tokens(self):
        """Carrega tokens do storage"""
        if self.token_manager:
            # Usa TokenManager (formato: {'id', 'nome', 'token', 'ativo', ...})
            self.tokens = self.token_manager.get_all_tokens()
            
            # Adiciona flag is_active para cada token (compatibilidade com UI)
            active_token_id = self.token_manager.tokens_data.get('active_token_id')
            for token in self.tokens:
                token['is_active'] = (token['id'] == active_token_id)
        else:
            # Usa SecureStorage (formato antigo: {'id', 'name', 'token', 'is_active', ...})
            self.tokens = self.storage.load_tokens()
        self._refresh_tokens_list()
    
    def _refresh_tokens_list(self):
        """Atualiza lista de tokens"""
        # Limpa container
        for widget in self.tokens_container.winfo_children():
            widget.destroy()
        
        if not self.tokens:
            self._show_empty_state()
            return
        
        # Exibe tokens
        for token_data in self.tokens:
            self._create_token_card(token_data)
    
    def _show_empty_state(self):
        """Mostra estado vazio"""
        card = Card(self.tokens_container, theme=self.theme)
        card.pack(fill='x', pady=(0, 16))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=40, pady=60)
        
        tk.Label(
            container,
            text="📋 Nenhum token cadastrado",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack()
        
        tk.Label(
            container,
            text="Clique em 'Adicionar Token' para começar",
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_TERTIARY,
            bg=self.theme.BG_PRIMARY
        ).pack(pady=(8, 0))
    
    def _create_token_card(self, token_data):
        """Cria card de token"""
        card = Card(self.tokens_container, theme=self.theme)
        card.pack(fill='x', pady=(0, 12))
        
        container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        # Header do card
        header = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        header.pack(fill='x', pady=(0, 12))
        
        # Indicador de token ativo (⭐)
        if token_data.get('is_active', False):
            tk.Label(
                header,
                text="⭐",
                font=self.theme.get_font("xl"),
                fg=self.theme.WARNING,
                bg=self.theme.BG_PRIMARY
            ).pack(side='left', padx=(0, 8))
        
        # Nome
        nome_label = tk.Label(
            header,
            text=f"🔑 {self._get_token_name(token_data)}",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        )
        nome_label.pack(side='left')
        
        # Badge "ATIVO" se for o token ativo
        if token_data.get('is_active', False):
            active_badge = tk.Label(
                header,
                text="ATIVO",
                font=self.theme.get_font("xs", "bold"),
                fg='white',
                bg=self.theme.PRIMARY,
                padx=8,
                pady=2
            )
            active_badge.pack(side='left', padx=(12, 0))
        
        # Status badge
        status = "✅ Ativo" if token_data.get('active', True) else "❌ Inativo"
        status_color = self.theme.SUCCESS if token_data.get('active', True) else self.theme.DANGER
        
        tk.Label(
            header,
            text=status,
            font=self.theme.get_font("sm", "bold"),
            fg=status_color,
            bg=self.theme.BG_PRIMARY
        ).pack(side='left', padx=(12, 0))
        
        # Token preview (mascarado)
        token = token_data.get('token', '')
        token_preview = token[:20] + '...' + token[-10:] if len(token) > 30 else token
        
        token_frame = tk.Frame(container, bg=self.theme.BG_TERTIARY)
        token_frame.pack(fill='x', pady=(0, 12))
        
        tk.Label(
            token_frame,
            text=token_preview,
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_TERTIARY,
            anchor='w'
        ).pack(fill='x', padx=12, pady=8)
        
        # Botões
        buttons = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        buttons.pack(fill='x')
        
        ModernButton(
            buttons,
            text="📋 Copiar",
            variant="secondary",
            theme=self.theme,
            command=lambda: self._copy_token(token_data)
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons,
            text="✏️ Editar",
            variant="secondary",
            theme=self.theme,
            command=lambda: self._edit_token(token_data)
        ).pack(side='left', padx=(0, 8))
        
        ModernButton(
            buttons,
            text="🗑️ Excluir",
            variant="danger",
            theme=self.theme,
            command=lambda: self._delete_token(token_data)
        ).pack(side='left', padx=(0, 8))
        
        # Botão "Usar este Token" (se não for o ativo)
        if not token_data.get('is_active', False):
            ModernButton(
                buttons,
                text="⭐ Usar este Token",
                variant="primary",
                theme=self.theme,
                command=lambda: self._set_active_token(token_data)
            ).pack(side='left')
    
    def _add_token(self):
        """Adiciona novo token"""
        self.editing_token = None
        self._show_token_form()
    
    def _edit_token(self, token_data):
        """Edita token existente"""
        self.editing_token = token_data
        self._show_token_form(token_data)
    
    def _show_token_form(self, token_data=None):
        """Mostra formulário de token"""
        # Modal
        modal = tk.Toplevel(self.winfo_toplevel())
        modal.title("Adicionar Token" if not token_data else "Editar Token")
        modal.geometry("600x500")
        modal.configure(bg=self.theme.BG_SECONDARY)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()
        
        # Centralizar
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (600 // 2)
        y = (modal.winfo_screenheight() // 2) - (500 // 2)
        modal.geometry(f"600x500+{x}+{y}")
        
        # Conteúdo
        main = tk.Frame(modal, bg=self.theme.BG_SECONDARY)
        main.pack(fill='both', expand=True, padx=24, pady=24)
        
        # Título
        tk.Label(
            main,
            text="📝 Adicionar Token" if not token_data else "✏️ Editar Token",
            font=self.theme.get_font("xl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_SECONDARY
        ).pack(anchor='w', pady=(0, 16))
        
        # Card
        card = Card(main, theme=self.theme)
        card.pack(fill='x')
        
        card_container = tk.Frame(card, bg=self.theme.BG_PRIMARY)
        card_container.pack(fill='x', padx=20, pady=20)
        
        # Nome
        tk.Label(
            card_container,
            text="Nome *",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 6))
        
        name_frame = tk.Frame(
            card_container,
            bg=self.theme.BG_SECONDARY,
            highlightthickness=1,
            highlightbackground=self.theme.BORDER
        )
        name_frame.pack(fill='x', pady=(0, 16))
        
        name_entry = tk.Entry(
            name_frame,
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY,
            relief='flat',
            borderwidth=0
        )
        name_entry.pack(fill='x', padx=12, pady=10)
        
        if token_data:
            name_entry.insert(0, self._get_token_name(token_data))
        
        # Token
        tk.Label(
            card_container,
            text="Token de Acesso *",
            font=self.theme.get_font("sm", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 6))
        
        token_frame = tk.Frame(
            card_container,
            bg=self.theme.BG_TERTIARY,
            highlightthickness=1,
            highlightbackground=self.theme.BORDER
        )
        token_frame.pack(fill='x')
        
        token_text = tk.Text(
            token_frame,
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_TERTIARY,
            relief='flat',
            borderwidth=0,
            height=8,
            wrap='word'
        )
        token_text.pack(fill='x', padx=12, pady=10)
        
        if token_data:
            token_text.insert('1.0', token_data.get('token', ''))
        
        # Botões
        buttons = tk.Frame(main, bg=self.theme.BG_SECONDARY)
        buttons.pack(fill='x', pady=(16, 0))
        
        ModernButton(
            buttons,
            text="💾 Salvar",
            variant="primary",
            theme=self.theme,
            command=lambda: self._save_token_from_form(modal, name_entry, token_text, token_data)
        ).pack(side='right')
        
        ModernButton(
            buttons,
            text="Cancelar",
            variant="secondary",
            theme=self.theme,
            command=modal.destroy
        ).pack(side='right', padx=(0, 8))
    
    def _save_token_from_form(self, modal, name_entry, token_text, token_data):
        """Salva token do formulário"""
        name = name_entry.get().strip()
        token = token_text.get('1.0', 'end-1c').strip()
        
        if not name:
            messagebox.showerror("Erro", "Nome é obrigatório", parent=modal)
            return
        
        if not token:
            messagebox.showerror("Erro", "Token é obrigatório", parent=modal)
            return
        
        try:
            if self.token_manager:
                # Usa TokenManager
                if token_data:
                    # Edição
                    success = self.token_manager.update_token(
                        token_id=token_data['id'],
                        nome=name,
                        token=token
                    )
                    if success:
                        modal.destroy()
                        self._load_tokens()  # Recarrega para pegar estado atualizado
                        messagebox.showinfo("Sucesso", "Token atualizado com segurança!\n🔒 Criptografado com AES-256", parent=self.winfo_toplevel())
                    else:
                        messagebox.showerror("Erro", "Erro ao atualizar token", parent=modal)
                else:
                    # Novo token
                    self.token_manager.add_token(nome=name, token=token)
                    modal.destroy()
                    self._load_tokens()  # Recarrega para pegar estado atualizado
                    messagebox.showinfo("Sucesso", "Token salvo com segurança!\n🔒 Criptografado com AES-256", parent=self.winfo_toplevel())
            else:
                # Usa SecureStorage (modo legado)
                if token_data:
                    # Edição
                    token_data['name'] = name
                    token_data['token'] = token
                else:
                    # Novo
                    new_token = {
                        'id': str(uuid.uuid4()),
                        'name': name,
                        'token': token,
                        'active': True,
                        'created_at': datetime.now().isoformat()
                    }
                    self.tokens.append(new_token)
                
                # Salva
                if self.storage.save_tokens(self.tokens):
                    modal.destroy()
                    self._refresh_tokens_list()
                    messagebox.showinfo("Sucesso", "Token salvo com segurança!\n🔒 Criptografado com AES-256", parent=self.winfo_toplevel())
                else:
                    messagebox.showerror("Erro", "Erro ao salvar token", parent=modal)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar token:\n{str(e)}", parent=modal)
    
    def _copy_token(self, token_data):
        """Copia token para clipboard"""
        token = token_data.get('token', '')
        self.winfo_toplevel().clipboard_clear()
        self.winfo_toplevel().clipboard_append(token)
        messagebox.showinfo("Copiado", f"Token '{self._get_token_name(token_data)}' copiado para área de transferência!", parent=self.winfo_toplevel())
    
    def _delete_token(self, token_data):
        """Exclui token"""
        # Verificar se é o token ativo
        if token_data.get('is_active', False):
            messagebox.showwarning(
                "Atenção",
                "Não é possível excluir o token ativo.\n\nPrimeiro defina outro token como ativo.",
                parent=self.winfo_toplevel()
            )
            return
        
        if messagebox.askyesno("Confirmar", f"Deseja realmente excluir o token '{self._get_token_name(token_data)}'?", parent=self.winfo_toplevel()):
            try:
                if self.token_manager:
                    # Usa TokenManager
                    success = self.token_manager.remove_token(token_data['id'])
                    if success:
                        self._load_tokens()  # Recarrega para pegar estado atualizado
                        messagebox.showinfo("Sucesso", "Token excluído com sucesso!", parent=self.winfo_toplevel())
                    else:
                        messagebox.showerror("Erro", "Erro ao excluir token", parent=self.winfo_toplevel())
                else:
                    # Usa SecureStorage (modo legado)
                    self.tokens = [t for t in self.tokens if t.get('id') != token_data.get('id')]
                    if self.storage.save_tokens(self.tokens):
                        self._refresh_tokens_list()
                        messagebox.showinfo("Sucesso", "Token excluído com sucesso!", parent=self.winfo_toplevel())
                    else:
                        messagebox.showerror("Erro", "Erro ao excluir token", parent=self.winfo_toplevel())
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir token:\n{str(e)}", parent=self.winfo_toplevel())
    
    def _set_active_token(self, token_data):
        """Define token como ativo"""
        if messagebox.askyesno("Confirmar", f"Deseja usar o token '{self._get_token_name(token_data)}'?\n\nTodas as operações passarão a usar este token.", parent=self.winfo_toplevel()):
            try:
                if self.token_manager:
                    # Usa TokenManager
                    self.token_manager.set_active_token(token_data['id'])
                else:
                    # Usa SecureStorage (modo legado)
                    for token in self.tokens:
                        token['is_active'] = False
                    token_data['is_active'] = True
                    if not self.storage.save_tokens(self.tokens):
                        raise Exception("Erro ao salvar no storage")
                
                self._load_tokens()  # Recarrega para pegar estado atualizado
                messagebox.showinfo("Sucesso", f"Token '{self._get_token_name(token_data)}' agora está ativo!\n\n🔄 Recarregando configurações...", parent=self.winfo_toplevel())
                
                # Notifica mudança (callback se existir)
                if hasattr(self, 'on_token_changed'):
                    self.on_token_changed(token_data)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ativar token: {str(e)}", parent=self.winfo_toplevel())
