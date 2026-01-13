"""AIdrac - AI Out-of-Band Management. Alias for mcp-server-aidrac."""
try:
    from mcp_server_aidrac import *
    from mcp_server_aidrac import __version__
except ImportError:
    __version__ = "0.1.0"
