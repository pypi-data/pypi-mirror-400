from fastmcp import FastMCP
import random
import string

# 1. 定义服务名称
mcp = FastMCP("My Demo Tools")

# 2. 定义一个工具：生成随机密码
# @mcp.tool() 就像是把这个函数“挂”出去，让 AI 能看见
@mcp.tool()
def generate_password(length: int = 10) -> str:
    """
    生成一个指定长度的随机密码。
    Args:
        length: 密码的长度，默认为 10
    """
    # 这里是纯纯的本地逻辑，AI 根本不知道你是怎么算的
    chars = string.ascii_letters + string.digits + "!@#$%"
    password = "".join(random.choice(chars) for _ in range(length))
    return f"您的随机密码是: {password}"

# 3. 启动服务
if __name__ == "__main__":
    mcp.run()