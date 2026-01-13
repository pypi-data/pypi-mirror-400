import sys
from pathlib import Path

# Verifica --version ANTES de qualquer import
if '--version' in sys.argv:
    version_file = Path(__file__).parent / '__init__.py'
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                version = line.split('=')[1].strip().strip('"').strip("'")
                print(version)
                sys.exit(0)
    print("Error: __version__ not found")
    sys.exit(1)

def main():
    # Modo console: delega para __main_console__
    if '--console' in sys.argv or any(arg.startswith(('-p', '--payload', '-t=', '--a', '--database', '--dev')) for arg in sys.argv):
        from src import __main_console__
        __main_console__.main()
        return
    
    # Modo GUI: Dashboard Moderno em Tkinter
    try:
        from src.gui_main import run_gui
        run_gui()
    except ImportError as e:
        print(f"Erro ao importar interface gráfica: {e}")
        print("Use --console para modo console.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao iniciar interface gráfica: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
