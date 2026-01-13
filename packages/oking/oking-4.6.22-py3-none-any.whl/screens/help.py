"""
❓ Tela de Ajuda e Documentação - OKING Hub (Versão Integrada)
Sistema de ajuda com busca e tópicos
"""
import tkinter as tk
from tkinter import messagebox
from ui_components import ModernTheme, Card, ScrollableFrame


# ==================== COMPONENTES ====================

class HelpTopicCard(tk.Frame):
    """Card de tópico de ajuda clicável"""
    def __init__(self, parent, topic_data, theme=None, on_select=None):
        self.theme = theme or ModernTheme()
        super().__init__(
            parent,
            bg=self.theme.BG_PRIMARY,
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.theme.BORDER,
            cursor='hand2'
        )
        
        self.topic_data = topic_data
        self.on_select = on_select
        
        container = tk.Frame(self, bg=self.theme.BG_PRIMARY)
        container.pack(fill='both', expand=True, padx=16, pady=12)
        
        # Ícone e título
        header = tk.Frame(container, bg=self.theme.BG_PRIMARY)
        header.pack(fill='x', pady=(0, 4))
        
        tk.Label(
            header,
            text=f"{topic_data['icon']} {topic_data['title']}",
            font=self.theme.get_font("md", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w'
        ).pack(fill='x')
        
        # Descrição
        tk.Label(
            container,
            text=topic_data['description'],
            font=self.theme.get_font("sm"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY,
            anchor='w',
            wraplength=350,
            justify='left'
        ).pack(fill='x')
        
        self._setup_bindings()
    
    def _setup_bindings(self):
        """Configura hover e click"""
        widgets = [self] + self._get_all_children(self)
        
        for widget in widgets:
            widget.bind('<Enter>', self._on_enter)
            widget.bind('<Leave>', self._on_leave)
            widget.bind('<Button-1>', self._on_click)
    
    def _get_all_children(self, widget):
        """Retorna todos os widgets filhos recursivamente"""
        children = []
        for child in widget.winfo_children():
            children.append(child)
            children.extend(self._get_all_children(child))
        return children
    
    def _on_enter(self, e):
        self.configure(bg=self.theme.BG_HOVER, highlightbackground=self.theme.PRIMARY)
        for widget in self._get_all_children(self):
            try:
                widget.configure(bg=self.theme.BG_HOVER)
            except:
                pass
    
    def _on_leave(self, e):
        self.configure(bg=self.theme.BG_PRIMARY, highlightbackground=self.theme.BORDER)
        for widget in self._get_all_children(self):
            try:
                widget.configure(bg=self.theme.BG_PRIMARY)
            except:
                pass
    
    def _on_click(self, e):
        if self.on_select:
            self.on_select(self.topic_data)


# ==================== TELA PRINCIPAL ====================

class HelpScreen(tk.Frame):
    """Tela de ajuda integrada"""
    
    def __init__(self, parent, theme=None):
        self.theme = theme if theme else ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY)
        
        self.topics = self._get_help_topics()
        self.filtered_topics = self.topics.copy()
        self.current_topic = None
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._search_topics())
        
        self._build_ui()
    
    def _build_ui(self):
        """Constrói interface"""
        # Container principal
        main_container = tk.Frame(self, bg=self.theme.BG_SECONDARY)
        main_container.pack(fill='both', expand=True, padx=24, pady=24)
        
        # Header
        self._build_header(main_container)
        
        # Conteúdo (duas colunas)
        content = tk.Frame(main_container, bg=self.theme.BG_SECONDARY)
        content.pack(fill='both', expand=True, pady=(16, 0))
        
        # Coluna esquerda: Lista de tópicos
        self._build_topics_panel(content)
        
        # Coluna direita: Conteúdo
        self._build_content_panel(content)
    
    def _build_header(self, parent):
        """Cabeçalho"""
        header = Card(parent, theme=self.theme)
        header.pack(fill='x')
        
        container = tk.Frame(header, bg=self.theme.BG_PRIMARY)
        container.pack(fill='x', padx=20, pady=16)
        
        tk.Label(
            container,
            text="❓ Ajuda e Documentação",
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w')
        
        tk.Label(
            container,
            text="Documentação completa e suporte",
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(4, 0))
    
    def _build_topics_panel(self, parent):
        """Painel de tópicos (esquerda)"""
        topics_panel = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        topics_panel.pack(side='left', fill='both', expand=False, padx=(0, 12))
        topics_panel.configure(width=400)
        
        # Card de busca e tópicos
        topics_card = Card(topics_panel, theme=self.theme)
        topics_card.pack(fill='both', expand=True)
        topics_card.add_padding(20)
        
        # Busca
        tk.Label(
            topics_card,
            text="🔍 Buscar",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 12))
        
        search_frame = tk.Frame(topics_card, bg=self.theme.BG_TERTIARY, relief='flat')
        search_frame.pack(fill='x', pady=(0, 20))
        
        tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_TERTIARY,
            relief='flat',
            borderwidth=0
        ).pack(fill='x', ipady=10, padx=12, pady=10)
        
        # Título de tópicos
        tk.Label(
            topics_card,
            text="📚 Tópicos",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_PRIMARY
        ).pack(anchor='w', pady=(0, 12))
        
        # ScrollableFrame para tópicos
        topics_scroll = ScrollableFrame(topics_card, theme=self.theme)
        topics_scroll.pack(fill='both', expand=True)
        topics_scroll.configure(height=600)
        
        self.topics_container = topics_scroll.get_frame()
        self._render_topics()
    
    def _build_content_panel(self, parent):
        """Painel de conteúdo (direita)"""
        content_panel = tk.Frame(parent, bg=self.theme.BG_SECONDARY)
        content_panel.pack(side='left', fill='both', expand=True)
        
        # Card de conteúdo
        content_card = Card(content_panel, theme=self.theme)
        content_card.pack(fill='both', expand=True)
        content_card.add_padding(20)
        
        # ScrollableFrame para conteúdo
        content_scroll = ScrollableFrame(content_card, theme=self.theme)
        content_scroll.pack(fill='both', expand=True)
        
        self.content_container = content_scroll.get_frame()
        self._show_welcome()
    
    def _render_topics(self):
        """Renderiza lista de tópicos"""
        for widget in self.topics_container.winfo_children():
            widget.destroy()
        
        if not self.filtered_topics:
            tk.Label(
                self.topics_container,
                text="Nenhum tópico encontrado",
                font=self.theme.get_font("md"),
                fg=self.theme.TEXT_TERTIARY,
                bg=self.theme.BG_SECONDARY
            ).pack(pady=20)
        else:
            for topic in self.filtered_topics:
                HelpTopicCard(
                    self.topics_container,
                    topic_data=topic,
                    theme=self.theme,
                    on_select=self._show_topic
                ).pack(fill='x', pady=(0, 12))
    
    def _show_welcome(self):
        """Exibe tela de boas-vindas"""
        for widget in self.content_container.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.content_container,
            text="👋 Bem-vindo à Ajuda do OKING Hub",
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY
        ).pack(pady=(40, 20))
        
        tk.Label(
            self.content_container,
            text="Selecione um tópico ao lado para começar",
            font=self.theme.get_font("lg"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_SECONDARY
        ).pack(pady=(0, 40))
        
        # Dicas rápidas
        tips_frame = tk.Frame(self.content_container, bg=self.theme.BG_SECONDARY)
        tips_frame.pack(fill='x', padx=40)
        
        tk.Label(
            tips_frame,
            text="💡 Dicas Rápidas",
            font=self.theme.get_font("lg", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY
        ).pack(anchor='w', pady=(0, 16))
        
        tips = [
            "Use a busca para encontrar tópicos rapidamente",
            "Clique em qualquer tópico para ver detalhes",
            "Todos os recursos possuem documentação completa",
            "Verifique a seção 'Problemas Comuns' para soluções rápidas"
        ]
        
        for tip in tips:
            tip_frame = tk.Frame(tips_frame, bg=self.theme.INFO_BG, relief='flat')
            tip_frame.pack(fill='x', pady=(0, 8))
            
            tk.Label(
                tip_frame,
                text=f"• {tip}",
                font=self.theme.get_font("md"),
                fg=self.theme.INFO,
                bg=self.theme.INFO_BG,
                anchor='w',
                wraplength=600,
                justify='left'
            ).pack(padx=16, pady=12, fill='x')
    
    def _show_topic(self, topic_data):
        """Exibe conteúdo do tópico"""
        self.current_topic = topic_data
        
        for widget in self.content_container.winfo_children():
            widget.destroy()
        
        # Título
        tk.Label(
            self.content_container,
            text=f"{topic_data['icon']} {topic_data['title']}",
            font=self.theme.get_font("xxl", "bold"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY
        ).pack(anchor='w', pady=(20, 10))
        
        # Descrição
        tk.Label(
            self.content_container,
            text=topic_data['description'],
            font=self.theme.get_font("lg"),
            fg=self.theme.TEXT_SECONDARY,
            bg=self.theme.BG_SECONDARY,
            anchor='w',
            wraplength=700,
            justify='left'
        ).pack(anchor='w', pady=(0, 30))
        
        # Conteúdo
        content_text = tk.Text(
            self.content_container,
            font=self.theme.get_font("md"),
            fg=self.theme.TEXT_PRIMARY,
            bg=self.theme.BG_SECONDARY,
            relief='flat',
            borderwidth=0,
            wrap='word',
            height=25
        )
        content_text.pack(fill='both', expand=True, pady=(0, 20))
        content_text.insert('1.0', topic_data['content'])
        content_text.configure(state='disabled')
    
    def _search_topics(self):
        """Busca tópicos"""
        search = self.search_var.get().lower()
        
        if not search:
            self.filtered_topics = self.topics.copy()
        else:
            self.filtered_topics = [
                t for t in self.topics
                if search in t['title'].lower() or 
                   search in t['description'].lower() or
                   search in t['content'].lower()
            ]
        
        self._render_topics()
    
    def _get_help_topics(self):
        """Retorna tópicos de ajuda"""
        return [
            {
                'icon': '🚀',
                'title': 'Primeiros Passos',
                'description': 'Como começar a usar o OKING Hub',
                'content': '''Como Começar

1. Configuração Inicial
   • Acesse Setup → Configure seu shortname e token
   • As credenciais são salvas com criptografia AES-256
   • Token é necessário para todas as integrações

2. Configurar Banco de Dados
   • Vá em Configurações → Banco de Dados
   • Configure Oracle e/ou SQL Server
   • Teste a conexão antes de salvar

3. Gerenciar Tokens
   • Acesse Tokens → Adicione tokens de APIs
   • Suporta múltiplos tokens
   • Ative/desative conforme necessário

4. Configurar Jobs
   • Vá em Configuração de Jobs
   • Habilite/desabilite jobs
   • Configure SQL personalizado se necessário

Pronto! Agora você pode começar a usar o sistema.'''
            },
            {
                'icon': '🔧',
                'title': 'Configuração de Jobs',
                'description': 'Como configurar e gerenciar jobs de sincronização',
                'content': '''Configuração de Jobs

O que são Jobs?
Jobs são tarefas automatizadas que sincronizam dados entre sistemas.

Tipos de Jobs:
• Sincronizar Produtos
• Atualizar Preços
• Importar Pedidos
• Enviar Estoque
• Upload de Fotos

Como Configurar:
1. Acesse Configuração de Jobs
2. Selecione o job desejado
3. Ative/desative com o toggle
4. Edite SQL personalizado se necessário
5. Configure horário de execução
6. Salve as alterações

Boas Práticas:
• Teste antes de ativar em produção
• Use SQL otimizado
• Configure retry automático
• Monitore logs regularmente'''
            },
            {
                'icon': '🔐',
                'title': 'Segurança e Tokens',
                'description': 'Entenda como suas credenciais são protegidas',
                'content': '''Segurança e Criptografia

Criptografia de Dados:
• Algoritmo: AES-256 (Fernet)
• Key Derivation: PBKDF2-HMAC com SHA256
• Iterações: 100.000
• Chave única por máquina

O que é Criptografado?
• Tokens de API
• Senhas de banco de dados
• Credenciais de login

Armazenamento:
• Local: ~/.oking/
• Arquivos: config.json, tokens.json, database_config.json
• Permissões: Apenas usuário atual

Boas Práticas:
• Não compartilhe arquivos de configuração
• Use tokens com permissões mínimas
• Revogue tokens não utilizados
• Mantenha sistema atualizado'''
            },
            {
                'icon': '⚠️',
                'title': 'Problemas Comuns',
                'description': 'Soluções para problemas frequentes',
                'content': '''Problemas Comuns e Soluções

1. Erro de Conexão com Banco
   Solução:
   • Verifique credenciais
   • Teste conexão manualmente
   • Confirme firewall/portas
   • Valide string de conexão

2. Token Inválido
   Solução:
   • Regenere token na API
   • Atualize em Tokens
   • Verifique permissões
   • Confirme token ativo

3. Job não Executa
   Solução:
   • Verifique se está ativado
   • Confirme horário configurado
   • Veja logs de erro
   • Teste SQL manualmente

4. Lentidão no Sistema
   Solução:
   • Ative modo compacto
   • Reduza jobs paralelos
   • Limpe logs antigos
   • Otimize SQL dos jobs'''
            },
            {
                'icon': '📞',
                'title': 'Suporte',
                'description': 'Como obter ajuda adicional',
                'content': '''Suporte e Contato

Canais de Suporte:
📧 Email: suporte.b2c@openk.com.br
🌐 Site: www.openk.com.br

Horário de Atendimento:
• Segunda a Sexta: 8h às 18h
• Sábado: 9h às 13h

Antes de Contatar:
1. Verifique esta documentação
2. Consulte "Problemas Comuns"
3. Veja logs de erro
4. Prepare informações:
   • Versão do sistema
   • Descrição do problema
   • Passos para reproduzir

Feedback:
• Sugestões bem-vindas
• Reporte bugs
• Solicite recursos'''
            }
        ]
