"""
OKING Hub - Release GUI

Recria o fluxo do release.ps1 com interface gráfica em Python (Tkinter):
- Ler versão atual de src/__init__.py
- Selecionar incremento (major/minor/patch)
- Salvar nova versão
- Limpar builds anteriores (dist, build, oking.egg-info)
- Gerar wheel (setup.py sdist bdist_wheel)
- Upload para PyPI (python -m twine upload)

Execução:
  venv\\Scripts\\python.exe release_gui.py
  (ou python release_gui.py)
"""

from __future__ import annotations

import os
import re
import sys
import subprocess
import shutil
from pathlib import Path
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog


# ----------------------- Modern Theme -----------------------
class ModernTheme:
    # Colors
    PRIMARY = "#2563eb"
    PRIMARY_HOVER = "#1d4ed8"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    
    BG_PRIMARY = "#0f172a"
    BG_SECONDARY = "#1e293b"
    BG_TERTIARY = "#334155"
    BG_HOVER = "#475569"
    
    TEXT_PRIMARY = "#f8fafc"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    
    BORDER = "#334155"
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_SMALL = 9
    FONT_SIZE_LARGE = 12
    FONT_SIZE_TITLE = 14


class ModernButton(tk.Button):
    """Botão moderno customizado"""
    def __init__(self, parent, text="", command=None, style="primary", width=None, **kwargs):
        self.theme = ModernTheme()
        
        # Define cores baseado no estilo
        if style == "primary":
            bg, fg, hover_bg = self.theme.PRIMARY, self.theme.TEXT_PRIMARY, self.theme.PRIMARY_HOVER
        elif style == "success":
            bg, fg, hover_bg = self.theme.SUCCESS, self.theme.TEXT_PRIMARY, "#059669"
        elif style == "warning":
            bg, fg, hover_bg = self.theme.WARNING, self.theme.BG_PRIMARY, "#d97706"
        elif style == "danger":
            bg, fg, hover_bg = self.theme.DANGER, self.theme.TEXT_PRIMARY, "#dc2626"
        else:  # secondary
            bg, fg, hover_bg = self.theme.BG_TERTIARY, self.theme.TEXT_PRIMARY, self.theme.BG_HOVER
        
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            font=(self.theme.FONT_FAMILY, self.theme.FONT_SIZE_NORMAL, "bold"),
            relief=tk.FLAT,
            borderwidth=0,
            padx=20,
            pady=10,
            cursor="hand2",
            width=width,
            **kwargs
        )
        
        self.default_bg = bg
        self.hover_bg = hover_bg
        
        self.bind("<Enter>", lambda e: self.configure(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.configure(bg=self.default_bg))


class Card(tk.Frame):
    """Card container moderno"""
    def __init__(self, parent, **kwargs):
        theme = ModernTheme()
        super().__init__(
            parent,
            bg=theme.BG_SECONDARY,
            highlightbackground=theme.BORDER,
            highlightthickness=1,
            **kwargs
        )


class RadioCard(tk.Frame):
    """Radio button estilizado como card"""
    def __init__(self, parent, text, variable, value, command=None, **kwargs):
        self.theme = ModernTheme()
        super().__init__(parent, bg=self.theme.BG_SECONDARY, cursor="hand2")
        
        self.variable = variable
        self.value = value
        self.command = command
        self.selected = False
        
        # Radio visual (círculo)
        self.radio_canvas = tk.Canvas(
            self,
            width=20,
            height=20,
            bg=self.theme.BG_SECONDARY,
            highlightthickness=0
        )
        self.radio_canvas.pack(side=tk.LEFT, padx=(10, 8))
        
        # Label
        self.label = tk.Label(
            self,
            text=text,
            font=(self.theme.FONT_FAMILY, self.theme.FONT_SIZE_NORMAL),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY,
            cursor="hand2"
        )
        self.label.pack(side=tk.LEFT, padx=(0, 10), pady=8)
        
        # Bind clicks
        for widget in (self, self.radio_canvas, self.label):
            widget.bind("<Button-1>", lambda e: self.select())
        
        self.draw_radio()
        self.update_selection()
        
        # Monitor variable changes
        self.variable.trace_add("write", lambda *args: self.update_selection())
    
    def draw_radio(self):
        """Desenha círculo do radio"""
        self.radio_canvas.delete("all")
        # Círculo externo
        self.radio_canvas.create_oval(
            2, 2, 18, 18,
            outline=self.theme.BORDER if not self.selected else self.theme.PRIMARY,
            width=2
        )
        # Círculo interno (se selecionado)
        if self.selected:
            self.radio_canvas.create_oval(
                6, 6, 14, 14,
                fill=self.theme.PRIMARY,
                outline=self.theme.PRIMARY
            )
    
    def select(self):
        """Seleciona este radio"""
        self.variable.set(self.value)
        if self.command:
            self.command()
    
    def update_selection(self):
        """Atualiza visual baseado na seleção"""
        self.selected = (self.variable.get() == self.value)
        self.configure(bg=self.theme.BG_HOVER if self.selected else self.theme.BG_SECONDARY)
        self.radio_canvas.configure(bg=self.theme.BG_HOVER if self.selected else self.theme.BG_SECONDARY)
        self.label.configure(
            bg=self.theme.BG_HOVER if self.selected else self.theme.BG_SECONDARY,
            fg=self.theme.PRIMARY if self.selected else self.theme.TEXT_PRIMARY
        )
        self.draw_radio()


# ----------------------- Utilidades de log (thread-safe) -----------------------
class Logger:
    def __init__(self, text_widget: tk.Text) -> None:
        self._text = text_widget
        self._lock = threading.Lock()
        self.theme = ModernTheme()
        
        # Configurar tags de cores
        self._text.tag_configure("info", foreground=self.theme.TEXT_SECONDARY)
        self._text.tag_configure("ok", foreground=self.theme.SUCCESS)
        self._text.tag_configure("warn", foreground=self.theme.WARNING)
        self._text.tag_configure("error", foreground=self.theme.DANGER)
        self._text.tag_configure("step", foreground=self.theme.PRIMARY, font=("Consolas", 9, "bold"))

    def _append(self, msg: str, tag: str = "info") -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.insert(tk.END, msg, tag)
        self._text.see(tk.END)
        self._text.configure(state=tk.DISABLED)

    def info(self, msg: str) -> None:
        with self._lock:
            self._append(f"{msg}\n", "info")

    def ok(self, msg: str) -> None:
        with self._lock:
            self._append(f"✓ {msg}\n", "ok")

    def warn(self, msg: str) -> None:
        with self._lock:
            self._append(f"⚠ {msg}\n", "warn")

    def error(self, msg: str) -> None:
        with self._lock:
            self._append(f"✗ {msg}\n", "error")

    def step(self, title: str) -> None:
        with self._lock:
            self._append("\n" + "="*60 + "\n", "step")
            self._append(f"  {title}\n", "step")
            self._append("="*60 + "\n\n", "step")


# ----------------------------- Lógica de domínio ------------------------------
INIT_FILE = Path("src/__init__.py")


def detect_python_executable() -> str:
    venv_python = Path("venv/Scripts/python.exe") if os.name == "nt" else Path("venv/bin/python")
    if venv_python.exists():
        return str(venv_python)
    return sys.executable or "python"


def read_current_version(log: Logger) -> str | None:
    log.step("ETAPA 1: Lendo versão atual")
    if not INIT_FILE.exists():
        log.error(f"Arquivo {INIT_FILE.as_posix()} não encontrado!")
        return None
    content = INIT_FILE.read_text(encoding="utf-8")
    m = re.search(r"__version__\s*=\s*'(\d+)\.(\d+)\.(\d+)'", content)
    if not m:
        log.error(f"Não foi possível extrair a versão de {INIT_FILE.as_posix()}")
        return None
    current = f"{int(m.group(1))}.{int(m.group(2))}.{int(m.group(3))}"
    log.info(f"Versão atual: {current}")
    return current


def compute_new_version(current_version: str, inc: str) -> str:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", current_version)
    if not m:
        raise ValueError("Versão atual inválida")
    maj, min_, pat = map(int, m.groups())
    if inc == "major":
        maj, min_, pat = maj + 1, 0, 0
    elif inc == "minor":
        min_, pat = min_ + 1, 0
    else:
        pat = pat + 1
    return f"{maj}.{min_}.{pat}"


def save_new_version(log: Logger, old_version: str, new_version: str) -> bool:
    log.step(f"ETAPA 2: Incrementando versão ({old_version} → {new_version})")
    content = INIT_FILE.read_text(encoding="utf-8")
    updated = re.sub(
        rf"__version__\s*=\s*'{re.escape(old_version)}'",
        f"__version__ = '{new_version}'",
        content,
    )
    INIT_FILE.write_text(updated, encoding="utf-8")
    log.ok(f"Versão atualizada de {old_version} → {new_version}")
    return True


def clean_previous_builds(log: Logger) -> None:
    log.step("ETAPA 3: Limpando builds anteriores")
    for folder in ("dist", "build", "oking.egg-info"):
        p = Path(folder)
        if p.exists():
            log.info(f"Removendo diretório {folder}...")
            shutil.rmtree(p, ignore_errors=True)
    log.ok("Limpeza concluída")


def run_command(log: Logger, cmd: list[str]) -> int:
    log.info("Executando: " + " ".join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    assert proc.stdout is not None
    for line in proc.stdout:
        log.info(line.rstrip())
    proc.wait()
    return proc.returncode


def generate_wheel(log: Logger, python_exe: str, version: str) -> tuple[bool, Path | None, Path | None]:
    log.step("ETAPA 4: Gerando wheel (setup.py sdist bdist_wheel)")
    code = run_command(log, [python_exe, "setup.py", "sdist", "bdist_wheel"])
    if code != 0:
        log.error("Falha ao gerar wheel!")
        return False, None, None
    log.ok("Wheel gerada com sucesso!")
    tar_gz = Path("dist") / f"oking-{version}.tar.gz"
    whl = Path("dist") / f"oking-{version}-py3-none-any.whl"
    if not tar_gz.exists():
        log.error(f"Arquivo não encontrado: {tar_gz}")
        return False, None, None
    if not whl.exists():
        log.error(f"Arquivo não encontrado: {whl}")
        return False, None, None
    log.info("Arquivos gerados:")
    log.info(f"  - {tar_gz}")
    log.info(f"  - {whl}")
    return True, tar_gz, whl


def ensure_twine_installed(log: Logger, python_exe: str) -> bool:
    """Verifica se o twine está instalado; se não estiver, pergunta e instala."""
    # Verifica
    code = subprocess.call([python_exe, "-m", "pip", "show", "twine"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if code == 0:
        return True
    # Pergunta para instalar
    try:
        if not messagebox.askyesno("Dependência ausente", "Twine não está instalado no ambiente atual.\nDeseja instalar agora?\n\nComando: python -m pip install --upgrade pip setuptools wheel twine"):
            log.warn("Twine não instalado. Upload não poderá ser executado.")
            return False
    except Exception:
        # Em ambientes sem UI, segue com instalação
        pass
    log.step("Instalando dependências (pip, setuptools, wheel, twine)")
    install_cmd = [python_exe, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel", "twine"]
    rc = run_command(log, install_cmd)
    if rc != 0:
        log.error("Falha ao instalar twine. Instale manualmente: python -m pip install twine")
        return False
    return True


def upload_pypi(log: Logger, python_exe: str, tar_gz: Path, whl: Path, token: str) -> bool:
    log.step("ETAPA 6: Upload para PyPI (twine upload)")
    if not ensure_twine_installed(log, python_exe):
        return False
    # Usa autenticação não interativa: usuário __token__ e password = token
    cmd = [
        python_exe,
        "-m",
        "twine",
        "upload",
        "--non-interactive",
        "--username",
        "__token__",
        "--password",
        token,
        str(tar_gz),
        str(whl),
    ]
    code = run_command(log, cmd)
    if code != 0:
        log.error("Falha no upload!")
        log.warn("A versão foi atualizada mas o upload falhou")
        log.info("Para tentar novamente, execute:")
        log.info(f"  twine upload {tar_gz} {whl}")
        return False
    log.ok("Upload concluído!")
    return True


def run_git_merge_develop_into_main(log: Logger) -> bool:
    """Executa a sequência de git solicitada."""
    log.step("GIT: Atualizando main a partir de develop")
    # Verifica se git está disponível
    try:
        rc = subprocess.call(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        rc = 1
    if rc != 0:
        log.error("Git não encontrado no PATH. Instale o Git e tente novamente.")
        return False

    commands: list[list[str]] = [
        ["git", "checkout", "develop"],
        ["git", "pull"],
        ["git", "checkout", "main"],
        ["git", "merge", "develop"],
        ["git", "push", "origin", "main"],
    ]

    for cmd in commands:
        code = run_command(log, cmd)
        if code != 0:
            log.error(f"Comando falhou: {' '.join(cmd)}")
            return False
    log.ok("Branch main atualizado com sucesso.")
    return True


def run_git_commit_version(log: Logger, version: str) -> bool:
    """Cria commit da versão atualizada e envia para main."""
    log.step("GIT: Commit e push da nova versão")
    try:
        rc = subprocess.call(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        rc = 1
    if rc != 0:
        log.error("Git não encontrado no PATH. Commit não será realizado.")
        return False

    commands: list[list[str]] = [
        ["git", "add", "src/__init__.py"],
        ["git", "commit", "-m", f"Bump version to {version}"],
        ["git", "push", "origin", "main"],
    ]

    for cmd in commands:
        code = run_command(log, cmd)
        if code != 0:
            # Caso não haja mudanças para commit
            if cmd[1] == "commit":
                log.warn("Nenhuma alteração para commit. Prosseguindo.")
                continue
            log.error(f"Comando falhou: {' '.join(cmd)}")
            return False
    log.ok("Commit e push concluídos.")
    return True


# ---------------------------------- GUI --------------------------------------
class ReleaseApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.theme = ModernTheme()
        self.root.title("🚀 OKING Hub - Release Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg=self.theme.BG_PRIMARY)
        
        # Ícone da janela
        self._set_window_icon()

        self.python_exe = detect_python_executable()
        self.increment_type = tk.StringVar(value="patch")
        self.current_version_var = tk.StringVar(value="-")
        self.new_version_var = tk.StringVar(value="-")
        self._pypi_token: str | None = None

        self._build_ui()
        self._logger = Logger(self.txt_log)

        # Inicialização inicial
        self._update_current_version()
        self._compute_new_version()
    
    def _set_window_icon(self):
        """Define o ícone da janela"""
        try:
            icon_path = Path(__file__).parent / 'assets' / 'icon.ico'
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass

    # UI setup
    def _build_ui(self) -> None:
        # Container principal
        main_container = tk.Frame(self.root, bg=self.theme.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_frame = tk.Frame(main_container, bg=self.theme.BG_PRIMARY)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="🚀 Release Manager",
            font=(self.theme.FONT_FAMILY, 18, "bold"),
            bg=self.theme.BG_PRIMARY,
            fg=self.theme.TEXT_PRIMARY
        ).pack(side=tk.LEFT)
        
        # Card de versões
        version_card = Card(main_container)
        version_card.pack(fill=tk.X, pady=(0, 16))
        
        version_inner = tk.Frame(version_card, bg=self.theme.BG_SECONDARY)
        version_inner.pack(fill=tk.X, padx=20, pady=16)
        
        # Versão atual
        current_frame = tk.Frame(version_inner, bg=self.theme.BG_SECONDARY)
        current_frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            current_frame,
            text="Versão Atual:",
            font=(self.theme.FONT_FAMILY, self.theme.FONT_SIZE_NORMAL),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_SECONDARY
        ).pack(side=tk.LEFT)
        
        tk.Label(
            current_frame,
            textvariable=self.current_version_var,
            font=(self.theme.FONT_FAMILY, self.theme.FONT_SIZE_LARGE, "bold"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=(12, 0))
        
        # Versão nova
        new_frame = tk.Frame(version_inner, bg=self.theme.BG_SECONDARY)
        new_frame.pack(fill=tk.X)
        
        tk.Label(
            new_frame,
            text="Nova Versão:",
            font=(self.theme.FONT_FAMILY, self.theme.FONT_SIZE_NORMAL),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_SECONDARY
        ).pack(side=tk.LEFT)
        
        tk.Label(
            new_frame,
            textvariable=self.new_version_var,
            font=(self.theme.FONT_FAMILY, self.theme.FONT_SIZE_LARGE, "bold"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.PRIMARY
        ).pack(side=tk.LEFT, padx=(12, 0))
        
        # Card de tipo de incremento
        increment_card = Card(main_container)
        increment_card.pack(fill=tk.X, pady=(0, 16))
        
        tk.Label(
            increment_card,
            text="Tipo de Incremento",
            font=(self.theme.FONT_FAMILY, self.theme.FONT_SIZE_NORMAL, "bold"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY
        ).pack(anchor=tk.W, padx=20, pady=(16, 12))
        
        radio_container = tk.Frame(increment_card, bg=self.theme.BG_SECONDARY)
        radio_container.pack(fill=tk.X, padx=20, pady=(0, 16))
        
        for label in ["major", "minor", "patch"]:
            RadioCard(
                radio_container,
                text=label.upper(),
                variable=self.increment_type,
                value=label,
                command=self._compute_new_version
            ).pack(side=tk.LEFT, padx=(0, 8))
        
        # Botões principais
        btn_container = tk.Frame(main_container, bg=self.theme.BG_PRIMARY)
        btn_container.pack(fill=tk.X, pady=(0, 16))
        
        ModernButton(btn_container, text="🎯 Executar TUDO", command=self._run_all, style="primary").pack(side=tk.RIGHT, padx=(8, 0))
        ModernButton(btn_container, text="📤 Upload PyPI", command=self._upload, style="success").pack(side=tk.RIGHT, padx=(8, 0))
        ModernButton(btn_container, text="🔨 Gerar Wheel", command=self._build, style="secondary").pack(side=tk.RIGHT, padx=(8, 0))
        ModernButton(btn_container, text="🧹 Limpar Builds", command=self._clean, style="secondary").pack(side=tk.RIGHT, padx=(8, 0))
        
        # Botões secundários
        btn_container2 = tk.Frame(main_container, bg=self.theme.BG_PRIMARY)
        btn_container2.pack(fill=tk.X, pady=(0, 16))
        
        ModernButton(btn_container2, text="🔄 Git Merge", command=self._git_merge, style="secondary").pack(side=tk.LEFT)
        ModernButton(btn_container2, text="💾 Salvar Versão", command=self._save_version, style="secondary").pack(side=tk.LEFT, padx=(8, 0))
        ModernButton(btn_container2, text="🔍 Ler Versão", command=self._update_current_version, style="secondary").pack(side=tk.LEFT, padx=(8, 0))
        
        # Log
        log_card = Card(main_container)
        log_card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            log_card,
            text="📋 Log de Execução",
            font=(self.theme.FONT_FAMILY, self.theme.FONT_SIZE_NORMAL, "bold"),
            bg=self.theme.BG_SECONDARY,
            fg=self.theme.TEXT_PRIMARY
        ).pack(anchor=tk.W, padx=20, pady=(16, 12))
        
        log_inner = tk.Frame(log_card, bg=self.theme.BG_SECONDARY)
        log_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))
        
        self.txt_log = tk.Text(
            log_inner,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg=self.theme.BG_PRIMARY,
            fg=self.theme.TEXT_PRIMARY,
            insertbackground=self.theme.TEXT_PRIMARY,
            selectbackground=self.theme.PRIMARY,
            selectforeground=self.theme.TEXT_PRIMARY,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=12,
            pady=12
        )
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    # Helpers
    def _ask_token(self) -> str | None:
        if self._pypi_token:
            return self._pypi_token
        token = simpledialog.askstring(
            "Token PyPI",
            "Informe o token do PyPI (começa com pypi-...):",
            show='*',
            parent=self.root,
        )
        if token:
            self._pypi_token = token.strip()
        return self._pypi_token

    def _update_current_version(self) -> None:
        def task():
            v = read_current_version(self._logger)
            if v:
                self.current_version_var.set(v)
                # Calcular nova versão automaticamente após carregar a atual
                self.root.after(100, self._compute_new_version)
        threading.Thread(target=task, daemon=True).start()

    def _compute_new_version(self) -> None:
        cur = self.current_version_var.get()
        if cur and cur != "-":
            try:
                self.new_version_var.set(compute_new_version(cur, self.increment_type.get()))
            except Exception:
                self.new_version_var.set("-")

    def _save_version(self) -> None:
        cur = self.current_version_var.get()
        new = self.new_version_var.get()
        if cur in ("-", "") or new in ("-", ""):
            messagebox.showwarning("Atenção", "Versões inválidas para salvar.")
            return
        def task():
            if save_new_version(self._logger, cur, new):
                self.current_version_var.set(new)
        threading.Thread(target=task, daemon=True).start()

    def _clean(self) -> None:
        threading.Thread(target=lambda: clean_previous_builds(self._logger), daemon=True).start()

    def _build(self) -> None:
        def task():
            version = self.current_version_var.get()
            if version in ("-", ""):
                self._logger.warn("Versão atual desconhecida. Leia/Salve a versão primeiro.")
                return
            ok, tar_gz, whl = generate_wheel(self._logger, self.python_exe, version)
            if ok:
                self._last_artifacts = (tar_gz, whl)
        threading.Thread(target=task, daemon=True).start()

    def _upload(self) -> None:
        token = self._ask_token()
        if not token:
            self._logger.warn("Upload cancelado: token não informado.")
            return
        def task(token_val: str):
            version = self.current_version_var.get()
            if version in ("-", ""):
                self._logger.warn("Versão atual desconhecida. Leia/Salve a versão primeiro.")
                return
            tar_gz = Path("dist") / f"oking-{version}.tar.gz"
            whl = Path("dist") / f"oking-{version}-py3-none-any.whl"
            if not tar_gz.exists() or not whl.exists():
                self._logger.error("Artefatos não encontrados em dist/. Gere a wheel primeiro.")
                return
            if upload_pypi(self._logger, self.python_exe, tar_gz, whl, token_val):
                self._logger.info(f"Versão publicada: {version}")
                self._logger.info(f"PyPI: https://pypi.org/project/oking/{version}/")
        threading.Thread(target=lambda: task(token), daemon=True).start()

    def _run_all(self) -> None:
        token = self._ask_token()
        if not token:
            self._logger.warn("Upload não será realizado: token não informado.")
        def task(token_val: str | None):
            # 0) Atualizar branch primeiro
            if not run_git_merge_develop_into_main(self._logger):
                return
            # 1) Ler atual
            v = read_current_version(self._logger)
            if not v:
                return
            self.current_version_var.set(v)
            # 2) Calcular & salvar
            new_v = compute_new_version(v, self.increment_type.get())
            if not save_new_version(self._logger, v, new_v):
                return
            self.current_version_var.set(new_v)
            self.new_version_var.set(new_v)
            # 3) Limpar
            clean_previous_builds(self._logger)
            # 4) Build
            ok, tar_gz, whl = generate_wheel(self._logger, self.python_exe, new_v)
            if not ok:
                return
            # 5) Upload (confirmação via diálogo)
            uploaded = False
            if token_val and messagebox.askyesno("Confirmação", "Deseja fazer upload para o PyPI?"):
                uploaded = upload_pypi(self._logger, self.python_exe, tar_gz, whl, token_val)
            # 6) Commit por último (após upload)
            if uploaded:
                run_git_commit_version(self._logger, new_v)
            self._logger.ok("Processo concluído.")
        threading.Thread(target=lambda: task(token), daemon=True).start()

    def _git_merge(self) -> None:
        if not messagebox.askyesno(
            "Confirmar",
            "Executar sequência:\n\n"
            "git checkout develop\n"
            "git pull\n"
            "git checkout main\n"
            "git merge develop\n"
            "git push origin main\n\n"
            "Deseja continuar?",
        ):
            return
        threading.Thread(target=lambda: run_git_merge_develop_into_main(self._logger), daemon=True).start()


def main() -> int:
    root = tk.Tk()
    ReleaseApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


