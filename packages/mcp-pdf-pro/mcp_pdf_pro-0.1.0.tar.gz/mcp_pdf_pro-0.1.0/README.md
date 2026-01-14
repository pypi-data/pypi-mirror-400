# 📄 MCP PDF Pro - 智能视觉分析工具

这是一个基于 Model Context Protocol (MCP) 的 PDF 分析工具。它能通过 AI 视觉模型（如智谱 GLM-4V、GPT-4o）“看懂” PDF 中的流程图、表格和图片。

## 🚀 安装与使用

本工具支持 **代码与配置分离**。作为使用者，你无需修改代码，只需在 Cursor/Claude 中配置自己的 API Key 即可。

### 1. 配置 Cursor (推荐)

请将以下内容添加到你的 Cursor `settings.json` 的 `mcpServers` 字段中：

```json
{
  "mcpServers": {
    "PDFPro": {
      "command": "uvx",
      "args": [
        "--from",
        "/这里填你whl文件的绝对路径/mcp_pdf_pro-0.1.0-py3-none-any.whl",
        "mcp-pdf-pro"
      ],
      "env": {
        "PYTHONUTF8": "1",
        
        // 🔥 【必填】请填入你的 API Key (智谱/OpenAI/DeepSeek 等)
        "MCP_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxx",

        // 🌍 【选填】API 地址 (默认为智谱 GLM-4V，如需改用其他模型请修改)
        "MCP_BASE_URL": "[https://open.bigmodel.cn/api/paas/v4/](https://open.bigmodel.cn/api/paas/v4/)",
        "MCP_MODEL_NAME": "glm-4v"
      },
      "type": "stdio"
    }
  }
}