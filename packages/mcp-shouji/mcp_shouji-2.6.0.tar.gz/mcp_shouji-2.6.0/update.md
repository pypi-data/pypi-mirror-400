[2026-01-08 19:33:25] - 專案重構完成：
- 項目名稱變更為 mcp-shouji
- 作者變更為 f
- 郵箱變更為 f@gamil.com
- 移除 AI 相關描述，改為"跨平台交互式反饋與命令執行工具"
- 重構源碼目錄結構 (src/mcp_shouji)
- 更新所有文檔與配置檔案
- 更新 GitHub Workflows
- 更新測試與腳本

[2026-01-08 20:35:00] - 測試與修復完成：
- 修復 `pyproject.toml` 依賴配置警告，遷移至 `dependency-groups`。
- 完成專案重命名為 `mcp-shouji` 的剩餘清理工作 (涵蓋源碼、文檔、建置腳本及靜態資源)。
- 實作並通過單元測試 (Unit Tests): Server Utils, I18n, Basic Imports。
- 實作並通過整合測試 (Integration Tests): MCP Tools 邏輯 (`interactive_feedback`, `get_system_info`)。
- 驗證 Web UI 靜態資源與桌面應用模組中的項目名稱引用已更新。

[2026-01-08 21:18:41] - 移除AI引用與server.py模組化重構：
- 重構 `server.py`：提取環境檢測邏輯至 `utils/env_utils.py`
- 重構 `server.py`：提取反饋處理邏輯至 `utils/feedback_utils.py`
- `server.py` 行數簡化至 <300 行
- 移除所有 Web 本地化文件中的 AI 引用 (zh-CN, zh-TW, en)
- 移除 HTML 模板和 JS 文件中的 AI 引用，改用中性術語
- 函數重命名: `updateAISummaryContent` -> `updateSummaryContent`
- 函數重命名: `getAISummary` -> `getSummary`
- i18n key 變更: `sessionManagement.aiSummary` -> `sessionManagement.summary`
- 通過 Python 語法檢查
[2026-01-08 21:38:02] - 修复feedback.html缺失JS引用问题：
  - 添加第三方库引用 (marked, DOMPurify)
  - 添加核心模块引用 (logger, utils, dom-utils, time-utils, status-utils)
  - 添加功能模块引用 (connection-monitor, websocket-manager, image-handler, settings-manager, ui-manager)
  - 添加会话管理模块引用 (session-manager, session-data-manager, session-ui-renderer, session-details-modal)
  - 添加其他模块引用 (prompt-manager, tab-manager, app.js)
  - 修正模块路径 (utils/目录下的工具模块, prompt/目录下的提示词模块)
  - 通过MCP协议真实测试验证WebSocket连接和反馈提交功能正常

[2026-01-08 21:50:08] - WebSocket连接修复与MCP配置更新：
  - 修复feedback.html缺失JS引用问题
  - 添加WebSocket连接失败时的备用连接机制
  - MCP工具: interactive_feedback, get_system_info
  - 添加mcp-shouji配置到Windsurf mcp_config.json
  - 配置端口: 9765, 语言: zh-CN

[2026-01-08 23:35:24] - 修复MCP工具被Windsurf封禁问题: 将interactive_feedback重命名为shouji, 移除强制性USAGE RULES描述, 改为中文中性描述

[2026-01-08 23:47:33] - 修复Web UI初始化失败问题: feedback.html缺少JS模块引用(file-upload-manager, prompt-modal, prompt-input-buttons, prompt-settings-ui, textarea-height-manager, audio/notification模块)
