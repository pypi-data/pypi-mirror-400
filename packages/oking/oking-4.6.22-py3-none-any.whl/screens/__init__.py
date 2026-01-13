"""
📦 Screens Module - OKING Hub
Módulo com todas as telas integradas do sistema
"""

# Importar apenas telas que existem
try:
    from .settings import SettingsScreen
except ImportError:
    SettingsScreen = None

try:
    from .help import HelpScreen
except ImportError:
    HelpScreen = None

try:
    from .reports import ReportsScreen
except ImportError:
    ReportsScreen = None

try:
    from .logs import LogsScreen
except ImportError:
    LogsScreen = None

try:
    from .jobs import JobsScreen
except ImportError:
    JobsScreen = None

try:
    from .database import DatabaseScreen
except ImportError:
    DatabaseScreen = None

try:
    from .tokens import TokensScreen
except ImportError:
    TokensScreen = None

try:
    from .photos import PhotosScreen
except ImportError:
    PhotosScreen = None

__all__ = [
    'SettingsScreen',
    'HelpScreen',
    'ReportsScreen',
    'LogsScreen',
    'JobsScreen',
    'DatabaseScreen',
    'TokensScreen',
    'PhotosScreen',
]
