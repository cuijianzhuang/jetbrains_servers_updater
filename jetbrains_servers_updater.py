import shodan
import os
from datetime import datetime
from typing import List

# 从环境变量获取 Shodan API 密钥
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')
#调试
# SHODAN_API_KEY = ''
# 输出文件路径
OUTPUT_FILE = "jetbrains_servers.txt"

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

def generate_html(servers: List[str]) -> None:
    """
    生成HTML页面展示服务器列表
    """
    if not servers:
        print("没有服务器数据，跳过生成HTML")
        return
        
    print(f"开始生成HTML，服务器数量: {len(servers)}")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JetBrains 激活服务器列表</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2b2b2b;
                text-align: center;
            }}
            .update-time {{
                color: #666;
                text-align: center;
                margin-bottom: 20px;
            }}
            .server-list {{
                list-style: none;
                padding: 0;
            }}
            .server-item {{
                padding: 10px;
                margin: 5px 0;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                word-break: break-all;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .server-item:hover {{
                background-color: #e9ecef;
            }}
            .copy-btn {{
                background-color: #007bff;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            .copy-btn:hover {{
                background-color: #0056b3;
            }}
            .copy-btn.copied {{
                background-color: #28a745;
            }}
            @media (max-width: 600px) {{
                body {{
                    padding: 10px;
                }}
                .server-item {{
                    font-size: 14px;
                }}
                .copy-btn {{
                    padding: 4px 8px;
                    font-size: 12px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>JetBrains 激活服务器列表</h1>
            <div class="update-time">更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            <ul class="server-list">
                {chr(10).join(f'''
                    <li class="server-item">
                        <span class="server-url">{server}</span>
                        <button class="copy-btn" onclick="copyToClipboard(this, '{server}')">复制</button>
                    </li>''' for server in servers)}
            </ul>
        </div>
        
        <script>
        function copyToClipboard(button, text) {{
            // 创建临时输入框
            const input = document.createElement('input');
            input.value = text;
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
            
            // 更新按钮状态
            button.textContent = '已复制';
            button.classList.add('copied');
            
            // 2秒后恢复按钮状态
            setTimeout(() => {{
                button.textContent = '复制';
                button.classList.remove('copied');
            }}, 2000);
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

def update_servers_file(servers: List[str]) -> None:
    """
    更新服务器列表文件
    """
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# JetBrains激活服务器列表\n")
            f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for server in servers:
                f.write(f"{server}\n")
        print(f"成功更新服务器列表，共{len(servers)}个服务器")
        
        # 生成HTML文件
        generate_html(servers)
        
        # 显示文件内容
        print("\n=== 服务器列表内容 ===")
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            print(f.read())
        print("=====================")
    except Exception as e:
        print(f"写入文件时出错: {str(e)}")

def main():
    print(f"开始更新服务器列表 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    servers = get_activation_servers()
    if servers:
        update_servers_file(servers)
    else:
        print("未获取到服务器，跳过更新")

if __name__ == "__main__":
    main() 