"""版本管理模块

此模块用于集中管理项目版本号，确保 pyproject.toml 和 __version__ 保持一致。
"""

try:
    from importlib.metadata import version
    __version__ = version("zonaite")
except ImportError:
    __version__ = "0.1.0" 