"""
超级今日热点 MCP 服务器 - BachStudio 版本
获取全网主流平台的新闻热点
"""

__version__ = "3.1.0"
__author__ = "BachStudio"
__email__ = "contact@bachstudio.com"

from .server import HotNewsAPI, app

__all__ = ["HotNewsAPI", "app", "__version__"]
