"""
TokenManager - Gerenciador de Tokens para OKING HUB
Gerencia múltiplos tokens com suporte a migração automática de arquivos legados
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import requests
from cryptography.fernet import Fernet
import hashlib


class TokenManager:
    """Gerenciador de tokens com suporte a múltiplos tokens e migração automática"""
    
    TOKENS_FILE = Path.home() / '.oking' / 'tokens.json'
    LEGACY_TOKEN_FILE = 'token.txt'
    LEGACY_SHORTNAME_FILE = 'shortname.txt'
    
    def __init__(self):
        """Inicializa o gerenciador de tokens"""
        self.tokens_data = {
            'active_token_id': None,
            'shortname': None,
            'base_url': None,  # URL customizada (ex: plugmartins.openk.com.br)
            'tokens': []
        }
        self._encryption_key = None
        self._ensure_directory()
        self._load_tokens()
        self._migrate_legacy_files()
    
    def _ensure_directory(self):
        """Garante que o diretório .oking existe"""
        self.TOKENS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_encryption_key(self) -> bytes:
        """Obtém ou cria chave de criptografia baseada na máquina"""
        if self._encryption_key:
            return self._encryption_key
        
        # Usa o hostname como base para a chave (consistente por máquina)
        import socket
        import base64
        hostname = socket.gethostname()
        # Gera chave determinística baseada no hostname
        key_material = hashlib.sha256(hostname.encode()).digest()
        # Fernet requer chave de 32 bytes codificada em base64
        self._encryption_key = base64.urlsafe_b64encode(key_material)
        return self._encryption_key
    
    def _encrypt(self, data: str) -> str:
        """Criptografa dados"""
        try:
            f = Fernet(self._get_encryption_key())
            return f.encrypt(data.encode()).decode()
        except:
            return data  # Fallback se criptografia falhar
    
    def _decrypt(self, data: str) -> str:
        """Descriptografa dados"""
        try:
            f = Fernet(self._get_encryption_key())
            decrypted = f.decrypt(data.encode()).decode()
            return decrypted
        except Exception as e:
            print(f"[ERROR TokenManager] Erro ao descriptografar: {e}")
            print(f"[DEBUG TokenManager] Data recebida: {data[:50]}...")
            return data  # Fallback se for texto não criptografado
    
    def _load_tokens(self):
        """Carrega tokens do arquivo JSON"""
        if self.TOKENS_FILE.exists():
            try:
                with open(self.TOKENS_FILE, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Garante estrutura completa
                    self.tokens_data = {
                        'active_token_id': loaded_data.get('active_token_id'),
                        'shortname': loaded_data.get('shortname'),
                        'base_url': loaded_data.get('base_url'),  # Carrega URL customizada
                        'tokens': loaded_data.get('tokens', [])
                    }
            except Exception as e:
                print(f"Erro ao carregar tokens: {e}")
                self.tokens_data = {
                    'active_token_id': None,
                    'shortname': None,
                    'base_url': None,
                    'tokens': []
                }
    
    def _save_tokens(self):
        """Salva tokens no arquivo JSON"""
        try:
            with open(self.TOKENS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.tokens_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar tokens: {e}")
    
    def _migrate_legacy_files(self):
        """Migra arquivos legados token.txt e shortname.txt para JSON"""
        # Se já existe JSON e tem tokens, não precisa migrar
        if self.tokens_data.get('tokens'):
            return
        
        # Verifica se existem arquivos legados
        token_file = Path(self.LEGACY_TOKEN_FILE)
        shortname_file = Path(self.LEGACY_SHORTNAME_FILE)
        
        if not token_file.exists():
            return
        
        print("🔄 Migrando arquivos legados para novo formato...")
        
        try:
            # Lê shortname
            shortname = None
            if shortname_file.exists():
                with open(shortname_file, 'r', encoding='utf-8') as f:
                    shortname = f.read().strip()
            
            # Lê tokens (formato: "nome#token" por linha)
            with open(token_file, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
            
            migrated_count = 0
            for line in lines:
                if not line.strip():
                    continue
                
                # Parse formato: "nome#token"
                if '#' in line:
                    nome, token = line.split('#', 1)
                    nome = nome.strip()
                    token = token.strip()
                else:
                    # Fallback: se não tem #, usa a linha inteira como token
                    nome = f"Token {len(self.tokens_data['tokens']) + 1}"
                    token = line.strip()
                
                # Adiciona token
                self.add_token(nome, token, save=False)
                migrated_count += 1
            
            # Define shortname ou base_url
            if shortname:
                # Detecta o tipo de configuração:
                # 1. "protec.oking.openk.com.br" → shortname padrão (extrai "protec")
                # 2. "plugmartins.openk.com.br" → URL customizada (sem .oking.)
                # 3. "protec" → shortname simples (sem pontos)
                
                if '.oking.' in shortname.lower():
                    # Caso 1: Formato legado completo "protec.oking.openk.com.br"
                    # Extrai apenas o shortname (primeira parte antes de .oking)
                    shortname_only = shortname.split('.oking.')[0]
                    self.tokens_data['shortname'] = shortname_only
                    self.tokens_data['base_url'] = None
                    print(f"📌 Migrado como shortname padrão: {shortname_only}")
                    
                elif '.' in shortname:
                    # Caso 2: URL customizada (tem ponto mas não tem .oking.)
                    # Exemplo: "plugmartins.openk.com.br"
                    self.tokens_data['shortname'] = None
                    self.tokens_data['base_url'] = shortname
                    print(f"📌 Migrado como URL customizada: {shortname}")
                    
                else:
                    # Caso 3: Shortname simples (sem pontos)
                    # Exemplo: "protec"
                    self.tokens_data['shortname'] = shortname
                    self.tokens_data['base_url'] = None
                    print(f"📌 Migrado como shortname simples: {shortname}")
            
            # Salva JSON
            self._save_tokens()
            
            # Remove arquivos legados
            token_file.unlink()
            print(f"✅ Arquivo {self.LEGACY_TOKEN_FILE} migrado e removido")
            
            if shortname_file.exists():
                shortname_file.unlink()
                print(f"✅ Arquivo {self.LEGACY_SHORTNAME_FILE} migrado e removido")
            
            print(f"✅ {migrated_count} token(s) migrado(s) com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro na migração: {e}")
    
    def add_token(self, nome: str, token: str, ativo: bool = True, save: bool = True) -> Dict:
        """
        Adiciona um novo token
        
        Args:
            nome: Nome descritivo do token
            token: Token de acesso
            ativo: Se o token está ativo
            save: Se deve salvar no arquivo
        
        Returns:
            Dict com dados do token adicionado
        """
        # Gera ID único
        token_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        # Cria token
        token_data = {
            'id': token_id,
            'nome': nome,
            'token': self._encrypt(token),
            'ativo': ativo,
            'criado_em': datetime.now().isoformat(),
            'ultimo_uso': None
        }
        
        # Adiciona à lista
        self.tokens_data['tokens'].append(token_data)
        
        # Se é o primeiro token, define como ativo
        if not self.tokens_data['active_token_id']:
            self.tokens_data['active_token_id'] = token_id
        
        if save:
            self._save_tokens()
        
        return token_data
    
    def remove_token(self, token_id: str) -> bool:
        """
        Remove um token
        
        Args:
            token_id: ID do token
        
        Returns:
            True se removido com sucesso
        """
        # Remove da lista
        self.tokens_data['tokens'] = [
            t for t in self.tokens_data['tokens']
            if t['id'] != token_id
        ]
        
        # Se era o token ativo, seleciona outro
        if self.tokens_data['active_token_id'] == token_id:
            if self.tokens_data['tokens']:
                self.tokens_data['active_token_id'] = self.tokens_data['tokens'][0]['id']
            else:
                self.tokens_data['active_token_id'] = None
        
        self._save_tokens()
        return True
    
    def update_token(self, token_id: str, nome: Optional[str] = None, 
                     token: Optional[str] = None, ativo: Optional[bool] = None) -> bool:
        """
        Atualiza um token existente
        
        Args:
            token_id: ID do token
            nome: Novo nome (opcional)
            token: Novo token (opcional)
            ativo: Novo status (opcional)
        
        Returns:
            True se atualizado com sucesso
        """
        for t in self.tokens_data['tokens']:
            if t['id'] == token_id:
                if nome is not None:
                    t['nome'] = nome
                if token is not None:
                    t['token'] = self._encrypt(token)
                if ativo is not None:
                    t['ativo'] = ativo
                
                self._save_tokens()
                return True
        return False
    
    def set_active_token(self, token_id: str) -> bool:
        """
        Define o token ativo
        
        Args:
            token_id: ID do token
        
        Returns:
            True se definido com sucesso
        """
        # Verifica se token existe
        token_exists = any(t['id'] == token_id for t in self.tokens_data['tokens'])
        
        if token_exists:
            self.tokens_data['active_token_id'] = token_id
            
            # Atualiza último uso
            for t in self.tokens_data['tokens']:
                if t['id'] == token_id:
                    t['ultimo_uso'] = datetime.now().isoformat()
                    break
            
            self._save_tokens()
            return True
        return False
    
    def get_active_token(self) -> Optional[Dict]:
        """
        Obtém o token ativo
        
        Returns:
            Dict com dados do token ativo ou None
        """
        if not self.tokens_data['active_token_id']:
            return None
        
        for token in self.tokens_data['tokens']:
            if token['id'] == self.tokens_data['active_token_id']:
                # Retorna cópia com token descriptografado
                token_copy = token.copy()
                token_copy['token'] = self._decrypt(token['token'])
                return token_copy
        return None
    
    def get_all_tokens(self) -> List[Dict]:
        """
        Obtém todos os tokens
        
        Returns:
            Lista de tokens (com tokens descriptografados)
        """
        tokens = []
        for token in self.tokens_data['tokens']:
            token_copy = token.copy()
            # Só descriptografar se o token estiver criptografado
            if 'token' in token:
                token_copy['token'] = self._decrypt(token['token'])
            tokens.append(token_copy)
        return tokens
    
    def get_shortname(self) -> Optional[str]:
        """Obtém o shortname configurado"""
        return self.tokens_data.get('shortname')
    
    def set_shortname(self, shortname: str):
        """Define o shortname"""
        self.tokens_data['shortname'] = shortname
        self._save_tokens()
    
    def get_base_url(self) -> Optional[str]:
        """
        Obtém a URL base configurada.
        Retorna URL customizada se existir, senão monta com shortname.
        
        Returns:
            URL base completa ou None
        """
        # Prioridade 1: URL customizada
        if self.tokens_data.get('base_url'):
            return self.tokens_data['base_url']
        
        # Prioridade 2: Monta com shortname (formato legado)
        shortname = self.tokens_data.get('shortname')
        if shortname:
            return f"{shortname}.oking.openk.com.br"
        
        return None
    
    def set_base_url(self, base_url: Optional[str]):
        """
        Define URL base customizada.
        
        Args:
            base_url: URL base customizada (ex: plugmartins.openk.com.br) ou None para usar shortname
        """
        self.tokens_data['base_url'] = base_url
        self._save_tokens()
    
    def validate_shortname(self, shortname: str, custom_url: Optional[str] = None) -> tuple[bool, str]:
        """
        Valida um shortname ou URL customizada fazendo ping na API
        
        Args:
            shortname: Shortname a validar (usado se custom_url for None)
            custom_url: URL customizada (ex: plugmartins.openk.com.br)
        
        Returns:
            Tuple (sucesso, mensagem)
        """
        try:
            # Determina qual URL usar
            if custom_url:
                url = f'https://{custom_url}/api/consulta/ping'
            else:
                url = f'https://{shortname}.oking.openk.com.br/api/consulta/ping'
            
            response = requests.get(url, timeout=5)
            if response.ok:
                return True, "Configuração válida"
            else:
                return False, f"Erro: {response.text}"
        except requests.exceptions.Timeout:
            return False, "Tempo esgotado. Verifique sua conexão."
        except requests.exceptions.ConnectionError:
            return False, "Erro de conexão. Verifique a URL e sua internet."
        except Exception as e:
            return False, f"Erro ao validar: {str(e)}"
    
    def validate_token(self, token: str, base_url: Optional[str] = None) -> tuple[bool, str, Optional[Dict]]:
        """
        Valida um token fazendo requisição na API
        
        Args:
            token: Token a validar
            base_url: URL base (usa a configurada se não informada)
        
        Returns:
            Tuple (sucesso, mensagem, dados_integracao)
        """
        if not base_url:
            base_url = self.get_base_url()
        
        if not base_url:
            return False, "URL base não configurada", None
        
        try:
            response = requests.get(
                f'https://{base_url}/api/consulta/integracao/filtros?token={token}',
                timeout=10
            )
            data = response.json()
            
            if data.get('sucesso'):
                return True, "Token válido", data.get('integracao')
            else:
                return False, data.get('mensagem', 'Token inválido'), None
                
        except requests.exceptions.Timeout:
            return False, "Tempo esgotado. Verifique sua conexão.", None
        except requests.exceptions.ConnectionError:
            return False, "Erro de conexão. Verifique sua internet.", None
        except Exception as e:
            return False, f"Erro ao validar: {str(e)}", None
    
    def has_tokens(self) -> bool:
        """Verifica se há tokens configurados"""
        return bool(self.tokens_data.get('tokens'))
    
    def needs_setup(self) -> bool:
        """Verifica se precisa de configuração inicial"""
        shortname = self.get_shortname()
        base_url = self.get_base_url()
        has_tokens = self.has_tokens()
        print(f"[DEBUG TokenManager] shortname: {shortname}, base_url: {base_url}, has_tokens: {has_tokens}")
        # Precisa de setup se não tiver (shortname OU base_url) E tokens
        return (not shortname and not base_url) or not has_tokens
