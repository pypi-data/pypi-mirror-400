| Module Name | Relative Path | Functionality | Dependencies |
| :--- | :--- | :--- | :--- |
| mcp_shouji | src/mcp_shouji | Main package, MCP server implementation | fastmcp, uvicorn, fastapi |
| mcp_shouji.web | src/mcp_shouji/web | Web UI implementation, FastAPI routes | fastapi, jinja2 |
| mcp_shouji.desktop_app | src/mcp_shouji/desktop_app | Desktop application wrapper | tauri |
| mcp_shouji.utils | src/mcp_shouji/utils | Utility functions (error handling, resource management, env detection, feedback processing) | psutil |
| mcp_shouji.utils.env_utils | src/mcp_shouji/utils/env_utils.py | Environment detection (WSL, remote, encoding init) | - |
| mcp_shouji.utils.feedback_utils | src/mcp_shouji/utils/feedback_utils.py | Feedback processing (save, format, image handling) | mcp.types |
| scripts | scripts/ | Build and maintenance scripts | - |
| tests | tests/ | Unit and integration tests | pytest |
| mcp_shouji_desktop | src-tauri/python/mcp_shouji_desktop | Tauri Python extension | pyo3 |
