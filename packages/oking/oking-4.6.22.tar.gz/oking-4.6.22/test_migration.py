"""
Teste de migração de arquivos legados para tokens.json
Testa diferentes cenários de migração
"""

import os
import json
from pathlib import Path
import shutil

# Cleanup antes dos testes
def cleanup():
    """Remove arquivos de teste"""
    files_to_remove = [
        'token.txt',
        'shortname.txt',
        Path.home() / '.oking' / 'tokens.json'
    ]
    for f in files_to_remove:
        try:
            if Path(f).exists():
                Path(f).unlink()
                print(f"🗑️  Removido: {f}")
        except:
            pass

def create_legacy_files(shortname_content, token_content):
    """Cria arquivos legados para teste"""
    with open('shortname.txt', 'w', encoding='utf-8') as f:
        f.write(shortname_content)
    
    with open('token.txt', 'w', encoding='utf-8') as f:
        f.write(token_content)
    
    print(f"📝 Criados arquivos legados:")
    print(f"   shortname.txt: {shortname_content}")
    print(f"   token.txt: {token_content}")

def verify_migration(expected_shortname, expected_base_url):
    """Verifica se a migração foi bem-sucedida"""
    tokens_file = Path.home() / '.oking' / 'tokens.json'
    
    if not tokens_file.exists():
        print("❌ FALHA: tokens.json não foi criado!")
        return False
    
    with open(tokens_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n📊 Resultado da migração:")
    print(f"   shortname: {data.get('shortname')}")
    print(f"   base_url: {data.get('base_url')}")
    print(f"   tokens: {len(data.get('tokens', []))} token(s)")
    
    # Validações
    success = True
    
    if data.get('shortname') != expected_shortname:
        print(f"❌ shortname incorreto! Esperado: {expected_shortname}, Obtido: {data.get('shortname')}")
        success = False
    else:
        print(f"✅ shortname correto: {expected_shortname}")
    
    if data.get('base_url') != expected_base_url:
        print(f"❌ base_url incorreto! Esperado: {expected_base_url}, Obtido: {data.get('base_url')}")
        success = False
    else:
        print(f"✅ base_url correto: {expected_base_url}")
    
    if len(data.get('tokens', [])) == 0:
        print("❌ Nenhum token migrado!")
        success = False
    else:
        print(f"✅ {len(data.get('tokens', []))} token(s) migrado(s)")
    
    # Verifica se arquivos legados foram removidos
    if Path('token.txt').exists() or Path('shortname.txt').exists():
        print("❌ Arquivos legados não foram removidos!")
        success = False
    else:
        print("✅ Arquivos legados removidos")
    
    return success

def test_scenario_1():
    """Teste 1: Shortname padrão (formato antigo com .oking.)"""
    print("\n" + "="*70)
    print("TESTE 1: Shortname padrão - protec.oking.openk.com.br")
    print("="*70)
    
    cleanup()
    create_legacy_files(
        shortname_content="protec.oking.openk.com.br",
        token_content="Protec#ABC123XYZ"
    )
    
    # Importa TokenManager (faz a migração automaticamente)
    from src.token_manager import TokenManager
    token_manager = TokenManager()
    
    # Verifica resultado
    success = verify_migration(
        expected_shortname="protec",
        expected_base_url=None
    )
    
    # Testa get_base_url()
    base_url = token_manager.get_base_url()
    expected_url = "protec.oking.openk.com.br"
    
    if base_url == expected_url:
        print(f"✅ get_base_url() retornou: {base_url}")
    else:
        print(f"❌ get_base_url() incorreto! Esperado: {expected_url}, Obtido: {base_url}")
        success = False
    
    print("\n" + ("🎉 TESTE 1 PASSOU!" if success else "❌ TESTE 1 FALHOU!"))
    return success

def test_scenario_2():
    """Teste 2: URL customizada (sem .oking.)"""
    print("\n" + "="*70)
    print("TESTE 2: URL customizada - plugmartins.openk.com.br")
    print("="*70)
    
    cleanup()
    create_legacy_files(
        shortname_content="plugmartins.openk.com.br",
        token_content="PlugMartins#XYZ789ABC"
    )
    
    # Importa TokenManager (faz a migração automaticamente)
    # Precisa recarregar o módulo
    import importlib
    import src.token_manager
    importlib.reload(src.token_manager)
    from src.token_manager import TokenManager
    
    token_manager = TokenManager()
    
    # Verifica resultado
    success = verify_migration(
        expected_shortname=None,
        expected_base_url="plugmartins.openk.com.br"
    )
    
    # Testa get_base_url()
    base_url = token_manager.get_base_url()
    expected_url = "plugmartins.openk.com.br"
    
    if base_url == expected_url:
        print(f"✅ get_base_url() retornou: {base_url}")
    else:
        print(f"❌ get_base_url() incorreto! Esperado: {expected_url}, Obtido: {base_url}")
        success = False
    
    print("\n" + ("🎉 TESTE 2 PASSOU!" if success else "❌ TESTE 2 FALHOU!"))
    return success

def test_scenario_3():
    """Teste 3: Shortname simples (apenas 'protec')"""
    print("\n" + "="*70)
    print("TESTE 3: Shortname simples - protec")
    print("="*70)
    
    cleanup()
    create_legacy_files(
        shortname_content="protec",
        token_content="Protec#DEF456GHI"
    )
    
    # Importa TokenManager (faz a migração automaticamente)
    import importlib
    import src.token_manager
    importlib.reload(src.token_manager)
    from src.token_manager import TokenManager
    
    token_manager = TokenManager()
    
    # Verifica resultado (shortname simples deve ser tratado como shortname padrão)
    success = verify_migration(
        expected_shortname="protec",
        expected_base_url=None
    )
    
    # Testa get_base_url()
    base_url = token_manager.get_base_url()
    expected_url = "protec.oking.openk.com.br"
    
    if base_url == expected_url:
        print(f"✅ get_base_url() retornou: {base_url}")
    else:
        print(f"❌ get_base_url() incorreto! Esperado: {expected_url}, Obtido: {base_url}")
        success = False
    
    print("\n" + ("🎉 TESTE 3 PASSOU!" if success else "❌ TESTE 3 FALHOU!"))
    return success

def test_scenario_4():
    """Teste 4: Múltiplos tokens"""
    print("\n" + "="*70)
    print("TESTE 4: Múltiplos tokens")
    print("="*70)
    
    cleanup()
    create_legacy_files(
        shortname_content="protec",
        token_content="Protec#ABC123\nFilial1#DEF456\nFilial2#GHI789"
    )
    
    # Importa TokenManager (faz a migração automaticamente)
    import importlib
    import src.token_manager
    importlib.reload(src.token_manager)
    from src.token_manager import TokenManager
    
    token_manager = TokenManager()
    
    # Verifica resultado
    tokens_file = Path.home() / '.oking' / 'tokens.json'
    with open(tokens_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    success = True
    
    if len(data.get('tokens', [])) == 3:
        print(f"✅ 3 tokens migrados corretamente")
    else:
        print(f"❌ Esperado 3 tokens, obtido: {len(data.get('tokens', []))}")
        success = False
    
    print("\n" + ("🎉 TESTE 4 PASSOU!" if success else "❌ TESTE 4 FALHOU!"))
    return success

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INICIANDO TESTES DE MIGRAÇÃO")
    print("="*70)
    
    results = []
    
    try:
        results.append(("Teste 1: Shortname padrão", test_scenario_1()))
        results.append(("Teste 2: URL customizada", test_scenario_2()))
        results.append(("Teste 3: Shortname simples", test_scenario_3()))
        results.append(("Teste 4: Múltiplos tokens", test_scenario_4()))
    except Exception as e:
        print(f"\n❌ ERRO DURANTE TESTES: {e}")
        import traceback
        traceback.print_exc()
    
    # Resumo
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {name}")
    
    total_passed = sum(1 for _, r in results if r)
    total_tests = len(results)
    
    print(f"\nResultado: {total_passed}/{total_tests} testes passaram")
    
    # Cleanup final
    cleanup()
    print("\n🧹 Arquivos de teste removidos")
