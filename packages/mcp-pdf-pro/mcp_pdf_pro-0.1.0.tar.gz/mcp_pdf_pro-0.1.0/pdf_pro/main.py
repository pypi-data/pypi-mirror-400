import os
import sys
import base64
import fitz  # PyMuPDF
from fastmcp import FastMCP
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

mcp = FastMCP("Universal PDF Reader")

# ==========================================
# 辅助函数: 图片转 Base64 (通用标准)
# ==========================================
def encode_image_from_pixmap(pix):
    """将 PDF 截图转换为 Base64 编码，这是大多数 API 接受的标准格式"""
    # 转换为 PNG 格式的 bytes
    img_bytes = pix.tobytes("png")
    # 编码为 base64 字符串
    base64_str = base64.b64encode(img_bytes).decode("utf-8")
    return base64_str

# ==========================================
# 工具 1: 本地快速读取 (不变)
# ==========================================
@mcp.tool()
def read_pdf_native(file_path: str) -> str:
    """[本地/快速] 读取 PDF 纯文本，不消耗 Token。适用于无图表文档。"""
    if not os.path.exists(file_path): return "❌ 文件不存在"
    try:
        doc = fitz.open(file_path)
        text_out = [f"文件名: {os.path.basename(file_path)}", f"页数: {len(doc)}"]
        for i, page in enumerate(doc):
            t = page.get_text().strip()
            text_out.append(f"\n--- 第 {i+1} 页 ---\n{t}" if t else f"\n--- 第 {i+1} 页 (无文本) ---")
        return "\n".join(text_out)
    except Exception as e: return f"❌ 读取错误: {str(e)}"

# ==========================================
# 工具 2: 万能视觉分析 (兼容所有模型)
# ==========================================
@mcp.tool()
def analyze_pdf_visually(
    file_path: str, 
    page_numbers: str = "1-3", 
    focus_prompt: str = ""
) -> str:
    """
    [AI/视觉] 使用配置的大模型分析 PDF 中的图片、表格和流程图。
    兼容性：支持 OpenAI, Gemini, Claude(via中转), 通义千问, DeepSeek, Kimi 等。
    
    Args:
        file_path: PDF 绝对路径
        page_numbers: 要分析的页码 (如 "1,3-5")
        focus_prompt: (可选) 你的具体问题
    """
    # 1. 尝试获取 Key，如果没有则读取 MCP_API_KEY
    api_key = os.getenv("OPENAI_API_KEY")
    # 2. 如果没获取到，返回一个“傻瓜式”的报错指引
    if not api_key:
        return (
            "❌ 错误: 未检测到 API Key。\n"
            "请在您的 MCP 客户端配置 (settings.json) 的 'env' 字段中添加 'MCP_API_KEY'。\n"
            "如果您是智谱用户，请填入您的智谱 API Key。"
        )
    api_key = os.getenv("MCP_API_KEY") # 统一叫 MCP_API_KEY，避免混淆
    base_url = os.getenv("MCP_BASE_URL") # 关键：不同厂商地址不同
    model_name = os.getenv("MCP_MODEL_NAME", "gpt-4o") # 默认模型

    if not api_key or not base_url:
        return "❌ 错误: 未配置 MCP_API_KEY 或 MCP_BASE_URL。请检查 .env 文件。"

    if not os.path.exists(file_path):
        return f"❌ 错误: 找不到文件 {file_path}"

    # 2. 解析页码
    pages = set()
    try:
        for p in page_numbers.split(','):
            if '-' in p:
                s, e = map(int, p.split('-'))
                pages.update(range(s-1, e))
            else:
                pages.add(int(p)-1)
    except: return "❌ 页码格式错误"

    sys.stderr.write(f"正在调用 [{model_name}] via [{base_url}]...\n")

    try:
        # 3. 初始化通用客户端
        client = OpenAI(api_key=api_key, base_url=base_url)
        doc = fitz.open(file_path)
        results = [f"🤖 视觉分析报告 (模型: {model_name})", "="*30]

        count = 0
        for i in sorted(list(pages)):
            if count >= 5: break # 安全限制
            if i >= len(doc): continue

            # 4. 渲染图片
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2倍清晰度
            b64_img = encode_image_from_pixmap(pix)

            # 5. 发送请求 (标准 OpenAI 视觉格式)
            sys.stderr.write(f"正在发送第 {i+1} 页...\n")
            
            prompt_text = "请详细分析这张图片内容。"
            if focus_prompt: prompt_text += f" 重点关注: {focus_prompt}"

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64_img}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            results.append(f"\n[第 {i+1} 页]\n{content}")
            count += 1
            
        return "\n".join(results)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ API 调用失败: {str(e)}\n请检查 BASE_URL 和 模型名称是否匹配。"

# ==========================================
# 启动入口 (请确保这几行在文件最末尾)
# ==========================================
if __name__ == "__main__":
    import sys
    # 打印一条日志，确认服务正在运行
    sys.stderr.write("🚀 MCP Server is running! Waiting for Cursor...\n")
    sys.stderr.flush()
    
    # 核心启动命令
    mcp.run(transport="stdio")