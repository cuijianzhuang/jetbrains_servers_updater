import shodan
import os
from datetime import datetime
import pytz
from typing import List
import requests

# 从环境变量获取 Shodan API 密钥
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')

#调试
# SHODAN_API_KEY = ''

# 输出文件路径
OUTPUT_FILE = "jetbrains_servers.txt"

def get_beijing_time():
    """
    获取北京时间
    
    Returns:
        str: 格式化的北京时间字符串
    """
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_time = datetime.now(beijing_tz)
    return beijing_time.strftime('%Y-%m-%d %H:%M:%S')

def get_activation_servers() -> List[str]:
    """
    使用Shodan API获取JetBrains激活服务器列表
    """
    try:
        if not SHODAN_API_KEY:
            raise ValueError("未设置 SHODAN_API_KEY 环境变量")
            
        api = shodan.Shodan(SHODAN_API_KEY)
        
        # 搜索查询
        query = 'Location: https://account.jetbrains.com/fls-auth'
        results = api.search(query)
        
        print(f"搜索结果: {len(results['matches'])} 个匹配项")
        
        servers = []
        for result in results['matches']:
            ip = result['ip_str']
            port = result.get('port', 443)
            
            # 构建服务器URL
            if port == 443:
                server_url = f"https://{ip}"
            else:
                server_url = f"http://{ip}:{port}"
            
            servers.append(server_url)
        
        print(f"处理后的服务器数量: {len(servers)}")
        return servers
    
    except Exception as e:
        print(f"获取服务器时出错: {str(e)}")
        return []

def generate_html(valid_servers: List[str], invalid_servers: List[str]) -> None:
    """
    生成美化后的HTML页面展示服务器列表和统计信息
    """
    total_servers = len(valid_servers) + len(invalid_servers)
    if total_servers == 0:
        print("没有服务器数据，跳过生成HTML")
        return
        
    print(f"开始生成HTML，总服务器数量: {total_servers}")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JetBrains 激活服务器列表</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary-color: #1a73e8;
                --success-color: #34a853;
                --error-color: #ea4335;
                --background-color: #f8f9fa;
                --card-background: #ffffff;
                --text-primary: #202124;
                --text-secondary: #5f6368;
                --border-radius: 12px;
                --transition: all 0.3s ease;
            }}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Inter', sans-serif;
                line-height: 1.6;
                background-color: var(--background-color);
                color: var(--text-primary);
            }}

            .container {{
                max-width: 1000px;
                margin: 2rem auto;
                padding: 0 1rem;
            }}

            .header {{
                text-align: center;
                margin-bottom: 2rem;
            }}

            .header h1 {{
                font-size: 2.5rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
                background: linear-gradient(45deg, var(--primary-color), var(--success-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}

            .update-time {{
                color: var(--text-secondary);
                font-size: 0.9rem;
            }}

            .stats-container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }}

            .stats-card {{
                background: var(--card-background);
                padding: 1.5rem;
                border-radius: var(--border-radius);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
                transition: var(--transition);
            }}

            .stats-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
            }}

            .stats-value {{
                font-size: 2rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }}

            .stats-label {{
                color: var(--text-secondary);
                font-size: 0.9rem;
            }}

            .servers-section {{
                background: var(--card-background);
                border-radius: var(--border-radius);
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}

            .section-title {{
                font-size: 1.5rem;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid var(--background-color);
            }}

            .server-list {{
                list-style: none;
            }}

            .server-item {{
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: var(--border-radius);
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: var(--transition);
            }}

            .valid {{
                background-color: rgba(52, 168, 83, 0.1);
                border: 1px solid rgba(52, 168, 83, 0.2);
            }}

            .invalid {{
                background-color: rgba(234, 67, 53, 0.1);
                border: 1px solid rgba(234, 67, 53, 0.2);
            }}

            .server-item:hover {{
                transform: translateX(5px);
            }}

            .server-url {{
                font-family: monospace;
                font-size: 0.95rem;
            }}

            .copy-btn {{
                background-color: var(--primary-color);
                color: white;
                border: none;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9rem;
                font-weight: 500;
                transition: var(--transition);
            }}

            .copy-btn:hover {{
                background-color: #1557b0;
                transform: scale(1.05);
            }}

            .copy-btn.copied {{
                background-color: var(--success-color);
            }}

            @media (max-width: 768px) {{
                .container {{
                    margin: 1rem auto;
                }}

                .header h1 {{
                    font-size: 2rem;
                }}

                .stats-card {{
                    padding: 1rem;
                }}

                .stats-value {{
                    font-size: 1.5rem;
                }}

                .servers-section {{
                    padding: 1rem;
                }}

                .server-item {{
                    flex-direction: column;
                    gap: 0.5rem;
                    text-align: center;
                }}

                .server-url {{
                    word-break: break-all;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>JetBrains 激活服务器列表</h1>
                <div class="update-time">更新时间: {get_beijing_time()}</div>
            </div>
            
            <div class="stats-container">
                <div class="stats-card">
                    <div class="stats-value">{total_servers}</div>
                    <div class="stats-label">总服务器数量</div>
                </div>
                <div class="stats-card">
                    <div class="stats-value" style="color: var(--success-color)">{len(valid_servers)}</div>
                    <div class="stats-label">有效服务器数量</div>
                </div>
                <div class="stats-card">
                    <div class="stats-value" style="color: var(--error-color)">{len(invalid_servers)}</div>
                    <div class="stats-label">无效服务器数量</div>
                </div>
            </div>

            <div class="servers-section">
                <h2 class="section-title">有效服务器</h2>
                <ul class="server-list">
                    {chr(10).join(f'''
                    <li class="server-item valid">
                        <span class="server-url">{server}</span>
                        <button class="copy-btn" onclick="copyToClipboard(this, '{server}')">复制</button>
                    </li>''' for server in valid_servers)}
                </ul>
            </div>

            <div class="servers-section">
                <h2 class="section-title">无效服务器</h2>
                <ul class="server-list">
                    {chr(10).join(f'''
                    <li class="server-item invalid">
                        <span class="server-url">{server}</span>
                        <button class="copy-btn" onclick="copyToClipboard(this, '{server}')">复制</button>
                    </li>''' for server in invalid_servers)}
                </ul>
            </div>
        </div>
        
        <script>
        async function copyToClipboard(button, text) {{
            try {{
                await navigator.clipboard.writeText(text);
                button.textContent = '已复制';
                button.classList.add('copied');
                
                setTimeout(() => {{
                    button.textContent = '复制';
                    button.classList.remove('copied');
                }}, 2000);
            }} catch (err) {{
                console.error('复制失败:', err);
                button.textContent = '复制失败';
                setTimeout(() => {{
                    button.textContent = '复制';
                }}, 2000);
            }}
        }}
        </script>
    </body>
    </html>
    """
    
    try:
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("HTML文件已生成")
    except Exception as e:
        print(f"生成HTML文件时出错: {str(e)}")

def update_servers_file(servers: List[str], invalid_servers: List[str] = None) -> None:
    """
    更新服务器列表文件
    
    Args:
        servers: 有效服务器列表
        invalid_servers: 无效服务器列表（可选）
    """
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# JetBrains激活服务器列表\n")
            f.write(f"# 更新时间: {get_beijing_time()}\n\n")
            for server in servers:
                f.write(f"{server}\n")
        print(f"成功更新服务器列表，共{len(servers)}个有效服务器")
        
        # 生成HTML文件
        generate_html(servers, invalid_servers or [])
        
        # 显示文件内容
        print("\n=== 服务器列表内容 ===")
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            print(f.read())
        print("=====================")
    except Exception as e:
        print(f"写入文件时出错: {str(e)}")

def test_server(server_url):
    """
    测试服务器连接是否有效
    
    Args:
        server_url (str): 要测试的服务器URL
    
    Returns:
        bool: 如果服务器有效返回True，否则返回False
    """
    try:
        # 确保URL格式正确
        if not server_url.startswith(('http://', 'https://')):
            server_url = f'http://{server_url}'
            
        # 设置超时时间为5秒
        response = requests.get(server_url, timeout=5)
        
        # 检查响应状态码
        if response.status_code == 200:
            return True
        return False
    except (requests.RequestException, Exception) as e:
        print(f"测试服务器 {server_url} 时发生错误: {str(e)}")
        return False

def test_all_servers(servers_list):
    """
    测试所有服务器并返回有效的服务器列表
    
    Args:
        servers_list (list): 要测试的服务器URL列表
    
    Returns:
        tuple: (有效服务器列表, 无效服务器列表)
    """
    valid_servers = []
    invalid_servers = []
    
    # ANSI颜色代码
    GREEN_BG = '\033[42m'
    RED_BG = '\033[41m'
    WHITE_TEXT = '\033[37m'
    RESET = '\033[0m'
    
    for server in servers_list:
        print(f"正在测试服务器: {server}")
        if test_server(server):
            valid_servers.append(server)
            print(f"{GREEN_BG}{WHITE_TEXT}服务器 {server} 有效{RESET}")
        else:
            invalid_servers.append(server)
            print(f"{RED_BG}{WHITE_TEXT}服务器 {server} 无效{RESET}")
    
    return valid_servers, invalid_servers

def main():
    print(f"开始更新服务器列表 - {get_beijing_time()}")
    servers = get_activation_servers()
    if servers:
        # 先测试所有获取到的服务器
        print("\n开始测试服务器...")
        valid_servers, invalid_servers = test_all_servers(servers)
        
        # ANSI颜色代码
        GREEN_BG = '\033[42m'
        RED_BG = '\033[41m'
        WHITE_TEXT = '\033[37m'
        RESET = '\033[0m'
        
        print(f"\n测试完成！")
        print(f"统计信息:")
        print(f"- 总服务器数量: {len(servers)}")
        print(f"- 有效服务器数量: {len(valid_servers)}")
        print(f"- 无效服务器数量: {len(invalid_servers)}")
        
        print("\n所有服务器状态:")
        print("有效服务器:")
        for server in valid_servers:
            print(f"{GREEN_BG}{WHITE_TEXT}{server}{RESET}")
            
        print("\n无效服务器:")
        for server in invalid_servers:
            print(f"{RED_BG}{WHITE_TEXT}{server}{RESET}")
        
        # 只更新有效的服务器到文件
        if valid_servers:
            update_servers_file(valid_servers, invalid_servers)
        else:
            print("\n未找到有效的服务器，不更新文件")
    else:
        print("未获取到服务器，跳过更新")

if __name__ == "__main__":
    main() 