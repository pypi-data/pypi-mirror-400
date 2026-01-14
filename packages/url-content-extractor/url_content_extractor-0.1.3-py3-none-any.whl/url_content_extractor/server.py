from mcp.server.fastmcp import FastMCP
import httpx
from bs4 import BeautifulSoup
import traceback

# 1. 初始化 FastMCP 服务
mcp = FastMCP("url-content-extractor")

# 2. 定义工具
@mcp.tool()
async def fetch_url_content(url: str) -> str:
    """
    Fetch and extract the main text content from a given URL.
    
    Args:
        url: The URL of the webpage to fetch.
        
    Returns:
        The extracted plain text content of the page, or an error message.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除 script 和 style 元素
            for script in soup(["script", "style"]):
                script.extract()
                
            # 获取文本
            text = soup.get_text()
            
            # 清理空白字符
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text[:5000] # 限制返回长度，避免超出上下文窗口
            
    except Exception as e:
        return f"Error fetching URL: {str(e)}\n\n{traceback.format_exc()}"

# 3. 运行服务
def main():
    """Entry point for the package."""
    mcp.run()

if __name__ == "__main__":
    main()