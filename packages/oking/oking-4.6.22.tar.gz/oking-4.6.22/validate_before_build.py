"""
Script de validação pré-build para OKING HUB
Verifica sintaxe e importações antes de gerar nova versão

Uso: 
  Windows: venv\\Scripts\\python.exe validate_before_build.py
  Linux/Mac: venv/bin/python validate_before_build.py
  
Ou use o script build.ps1 que ativa automaticamente
"""

import sys
import py_compile
from pathlib import Path
import importlib.util
import subprocess
import os

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_header(msg):
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{msg}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

def check_venv():
    """Verifica se está rodando no ambiente virtual"""
    print_header("🔍 VERIFICANDO AMBIENTE VIRTUAL")
    
    # Verifica se está no venv
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print_success(f"Rodando no venv: {sys.prefix}")
        return True
    else:
        print_error("NÃO está rodando no ambiente virtual!")
        print(f"    Python atual: {sys.executable}")
        print(f"    Execute com: venv\\Scripts\\python.exe validate_before_build.py")
        print(f"    Ou use: .\\build.ps1")
        return False

def compile_file(file_path):
    """Compila arquivo Python para verificar sintaxe"""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def validate_syntax():
    """Valida sintaxe de todos os arquivos Python principais"""
    print_header("1️⃣  VALIDANDO SINTAXE DOS ARQUIVOS")
    
    files_to_check = [
        'src/__main__.py',
        'src/__init__.py',
        'src/utils.py',
        'src/jobs/receivables_jobs.py',
        'src/jobs/comission_jobs.py',
        'src/api/entities/contas_a_receber.py',
        'src/api/okinghub.py',
    ]
    
    errors = []
    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            print_warning(f"Arquivo não encontrado: {file_path}")
            continue
        
        success, error = compile_file(str(path))
        if success:
            print_success(f"Sintaxe OK: {file_path}")
        else:
            print_error(f"Erro de sintaxe em {file_path}")
            print(f"    {error}")
            errors.append(file_path)
    
    return len(errors) == 0

def validate_imports():
    """Valida importações principais"""
    print_header("2️⃣  VALIDANDO IMPORTAÇÕES")
    
    modules_to_test = [
        ('src.jobs.receivables_jobs', 'Job de Contas a Receber'),
        ('src.jobs.comission_jobs', 'Job de Comissão'),
        ('src.api.entities.contas_a_receber', 'Entity Contas a Receber'),
        ('src.utils', 'Utilitários'),
    ]
    
    errors = []
    for module_name, description in modules_to_test:
        try:
            # Tenta importar o módulo
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                print_error(f"Módulo não encontrado: {module_name} ({description})")
                errors.append(module_name)
            else:
                print_success(f"Importação OK: {module_name}")
        except Exception as e:
            print_error(f"Erro ao importar {module_name} ({description})")
            print(f"    {str(e)}")
            errors.append(module_name)
    
    return len(errors) == 0

def check_required_files():
    """Verifica se arquivos obrigatórios existem"""
    print_header("3️⃣  VERIFICANDO ARQUIVOS OBRIGATÓRIOS")
    
    required_files = [
        'setup.py',
        'pyproject.toml',
        'README.md',
        'src/__init__.py',
        'src/__main__.py',
        'src/jobs/receivables_jobs.py',
        'src/api/entities/contas_a_receber.py',
        'src/database/queries.py',
    ]
    
    missing = []
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print_success(f"Arquivo encontrado: {file_path}")
        else:
            print_error(f"Arquivo FALTANDO: {file_path}")
            missing.append(file_path)
    
    return len(missing) == 0

def main():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}🔍 VALIDAÇÃO PRÉ-BUILD - OKING HUB{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    all_ok = True
    
    # 0. Verificar se está no venv
    if not check_venv():
        all_ok = False
        print_header("⚠️  SOLUÇÃO")
        print_warning("Execute o script com o Python do venv:")
        print("    venv\\Scripts\\python.exe validate_before_build.py")
        print()
        print_warning("Ou use o script automatizado:")
        print("    .\\build.ps1")
        return 1
    
    # 1. Validar sintaxe
    if not validate_syntax():
        all_ok = False
    
    # 2. Validar importações
    if not validate_imports():
        all_ok = False
    
    # 3. Verificar arquivos obrigatórios
    if not check_required_files():
        all_ok = False
    
    # Resultado final
    print_header("📊 RESULTADO FINAL")
    if all_ok:
        print_success("TODAS AS VALIDAÇÕES PASSARAM!")
        print(f"{GREEN}{BOLD}✅ PODE GERAR A NOVA VERSÃO{RESET}")
        return 0
    else:
        print_error("FALHAS DETECTADAS!")
        print(f"{RED}{BOLD}❌ CORRIJA OS ERROS ANTES DE GERAR A VERSÃO{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
