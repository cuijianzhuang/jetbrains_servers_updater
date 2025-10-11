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
    生成美化后的Apple风格HTML页面展示服务器列表和统计信息
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
    <meta name="description" content="JetBrains 激活服务器状态监控 - 实时验证和管理激活服务器">
    <meta name="theme-color" content="#fbfbfd">
    <title>JetBrains 激活服务器</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-color: #0071e3;
            --primary-dark: #0077ED;
            --success-color: #30d158;
            --error-color: #ff3b30;
            --warning-color: #ff9500;
            --background-color: #fbfbfd;
            --card-background: #ffffff;
            --text-primary: #1d1d1f;
            --text-secondary: #86868b;
            --border-color: #d2d2d7;
            --border-radius: 18px;
            --transition: all 0.4s cubic-bezier(0.28, 0.11, 0.32, 1);
            --shadow-sm: 0 2px 10px rgba(0, 0, 0, 0.04);
            --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.08);
            --shadow-lg: 0 8px 30px rgba(0, 0, 0, 0.12);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.47059;
            letter-spacing: -0.022em;
            background: var(--background-color);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 0;
            overflow-x: hidden;
            opacity: 0;
            transition: opacity 0.5s ease;
        }}

        body.loaded {{
            opacity: 1;
        }}

        .container {{
            max-width: 980px;
            margin: 0 auto;
            padding: 0 22px;
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .hero-spacer {{
            height: 44px;
        }}

        .navbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 44px;
            background: rgba(251, 251, 253, 0.8);
            backdrop-filter: saturate(180%) blur(20px);
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            z-index: 9999;
            transition: var(--transition);
        }}

        .navbar.scrolled {{
            background: rgba(251, 251, 253, 0.95);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}

        .navbar-content {{
            max-width: 980px;
            margin: 0 auto;
            padding: 0 22px;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .navbar-brand {{
            font-size: 17px;
            line-height: 1.47059;
            font-weight: 600;
            letter-spacing: -0.022em;
            color: var(--text-primary);
        }}

        .navbar-links {{
            display: flex;
            gap: 32px;
        }}

        .navbar-links a {{
            font-size: 14px;
            line-height: 1.42859;
            font-weight: 400;
            letter-spacing: -0.016em;
            color: var(--text-primary);
            text-decoration: none;
            opacity: 0.8;
            transition: opacity 0.3s ease;
        }}

        .navbar-links a:hover {{
            opacity: 1;
        }}

        .header {{
            text-align: center;
            padding: 48px 0 36px;
            animation: fadeIn 0.8s ease-out;
        }}

        .header h1 {{
            font-size: 48px;
            line-height: 1.07143;
            font-weight: 600;
            letter-spacing: -0.005em;
            color: var(--text-primary);
            margin-bottom: 4px;
        }}

        .header .subtitle {{
            font-size: 24px;
            line-height: 1.14286;
            font-weight: 400;
            letter-spacing: 0.007em;
            color: var(--text-secondary);
            margin-top: 10px;
            margin-bottom: 12px;
        }}

        .update-time {{
            color: var(--text-secondary);
            font-size: 15px;
            line-height: 1.47059;
            font-weight: 400;
            letter-spacing: -0.022em;
            margin-top: 8px;
        }}

        .stats-container {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 48px;
            animation: fadeIn 0.8s ease-out 0.2s backwards;
        }}

        .stats-card {{
            background: var(--card-background);
            padding: 24px 16px;
            border-radius: var(--border-radius);
            border: 1px solid var(--border-color);
            text-align: center;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }}

        .stats-card:hover {{
            transform: scale(1.02);
            box-shadow: var(--shadow-md);
            border-color: rgba(0, 113, 227, 0.3);
        }}

        .stats-value {{
            font-size: 48px;
            line-height: 1.0625;
            font-weight: 600;
            letter-spacing: -0.009em;
            color: var(--text-primary);
            margin-bottom: 6px;
        }}

        .stats-card:nth-child(2) .stats-value {{
            color: var(--success-color);
        }}

        .stats-card:nth-child(3) .stats-value {{
            color: var(--error-color);
        }}

        .stats-label {{
            color: var(--text-secondary);
            font-size: 15px;
            line-height: 1.47059;
            font-weight: 400;
            letter-spacing: -0.022em;
        }}

        .servers-section {{
            margin-bottom: 40px;
            animation: fadeIn 0.8s ease-out 0.4s backwards;
        }}

        .section-title {{
            font-size: 32px;
            line-height: 1.1;
            font-weight: 600;
            letter-spacing: 0em;
            color: var(--text-primary);
            margin-bottom: 20px;
            text-align: left;
        }}

        .section-badge {{
            display: inline-block;
            font-size: 11px;
            line-height: 1.33337;
            font-weight: 600;
            letter-spacing: -0.01em;
            text-transform: uppercase;
            color: var(--success-color);
            margin-bottom: 6px;
        }}

        .servers-section:last-of-type .section-badge {{
            color: var(--error-color);
        }}

        .server-list {{
            list-style: none;
            display: grid;
            gap: 8px;
        }}

        .server-item {{
            background: var(--card-background);
            padding: 14px 18px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: var(--transition);
            position: relative;
        }}

        .server-item:hover {{
            box-shadow: var(--shadow-sm);
            border-color: rgba(0, 0, 0, 0.15);
        }}

        .valid:hover {{
            border-color: rgba(48, 209, 88, 0.4);
        }}

        .invalid:hover {{
            border-color: rgba(255, 59, 48, 0.4);
        }}

        .server-url {{
            font-family: 'SF Mono', 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.47059;
            font-weight: 400;
            letter-spacing: -0.016em;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .server-url::before {{
            content: '';
            width: 7px;
            height: 7px;
            border-radius: 50%;
            display: inline-block;
            flex-shrink: 0;
        }}

        .valid .server-url::before {{
            background: var(--success-color);
            box-shadow: 0 0 0 2px rgba(48, 209, 88, 0.2);
        }}

        .invalid .server-url::before {{
            background: var(--error-color);
            box-shadow: 0 0 0 2px rgba(255, 59, 48, 0.2);
        }}

        .copy-btn {{
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 6px 18px;
            border-radius: 980px;
            cursor: pointer;
            font-size: 14px;
            line-height: 1.47059;
            font-weight: 400;
            letter-spacing: -0.022em;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            gap: 5px;
            white-space: nowrap;
        }}

        .copy-btn:hover {{
            background: var(--primary-dark);
            transform: scale(0.98);
        }}

        .copy-btn:active {{
            transform: scale(0.96);
        }}

        .copy-btn.copied {{
            background: var(--success-color);
        }}

        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
                transform: scale(1);
            }}
            50% {{
                opacity: 0.8;
                transform: scale(0.98);
            }}
        }}

        .server-url::before {{
            animation: pulse 2s ease-in-out infinite;
        }}

        .footer {{
            text-align: center;
            padding: 40px 0 48px;
            border-top: 1px solid var(--border-color);
            margin-top: 48px;
        }}

        .footer p {{
            color: var(--text-secondary);
            font-size: 13px;
            line-height: 1.42859;
            font-weight: 400;
            letter-spacing: -0.016em;
        }}

        .footer strong {{
            color: var(--text-primary);
            font-weight: 500;
        }}

        .progress-bar {{
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--success-color));
            z-index: 10000;
            transition: width 0.3s ease;
            box-shadow: 0 0 10px rgba(0, 113, 227, 0.5);
        }}

        .back-to-top {{
            position: fixed;
            bottom: 40px;
            right: 40px;
            width: 48px;
            height: 48px;
            background: var(--card-background);
            border: 1px solid var(--border-color);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: var(--transition);
            box-shadow: var(--shadow-md);
            z-index: 999;
        }}

        .back-to-top.show {{
            opacity: 1;
            visibility: visible;
        }}

        .back-to-top:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: var(--primary-color);
        }}

        .back-to-top::before {{
            content: '↑';
            font-size: 24px;
            color: var(--text-primary);
        }}

        ::selection {{
            background: rgba(0, 113, 227, 0.2);
            color: var(--text-primary);
        }}

        ::-webkit-scrollbar {{
            width: 12px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--background-color);
        }}

        ::-webkit-scrollbar-thumb {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: 6px;
            border: 3px solid var(--background-color);
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(0, 0, 0, 0.3);
        }}

        @media (max-width: 1068px) {{
            .container {{
                padding: 0 48px;
            }}
        }}

        @media (max-width: 734px) {{
            .navbar-content {{
                padding: 0 16px;
            }}

            .navbar-links {{
                gap: 20px;
            }}

            .navbar-links a {{
                font-size: 12px;
            }}

            .container {{
                padding: 0 16px;
            }}

            .hero-spacer {{
                height: 44px;
            }}

            .header {{
                padding: 32px 0 28px;
            }}

            .header h1 {{
                font-size: 36px;
                line-height: 1.1;
                letter-spacing: -0.003em;
            }}

            .header .subtitle {{
                font-size: 19px;
                line-height: 1.19048;
                letter-spacing: 0.011em;
                margin-top: 8px;
            }}

            .update-time {{
                font-size: 13px;
            }}

            .stats-container {{
                grid-template-columns: 1fr;
                gap: 8px;
                margin-bottom: 32px;
            }}

            .stats-card {{
                padding: 20px 14px;
            }}

            .stats-value {{
                font-size: 40px;
            }}

            .stats-label {{
                font-size: 14px;
            }}

            .servers-section {{
                margin-bottom: 32px;
            }}

            .section-title {{
                font-size: 28px;
                margin-bottom: 16px;
            }}

            .server-item {{
                flex-direction: column;
                gap: 12px;
                align-items: stretch;
                padding: 12px 14px;
            }}

            .server-url {{
                word-break: break-all;
                font-size: 13px;
                justify-content: flex-start;
            }}

            .copy-btn {{
                width: 100%;
                justify-content: center;
                padding: 8px 18px;
            }}

            .footer {{
                padding: 32px 0 40px;
                margin-top: 32px;
            }}

            .back-to-top {{
                bottom: 20px;
                right: 20px;
                width: 44px;
                height: 44px;
            }}

            .back-to-top::before {{
                font-size: 20px;
            }}
        }}

    </style>
</head>
<body>
    <div class="progress-bar" id="progressBar" style="width: 0%"></div>
    
    <nav class="navbar">
        <div class="navbar-content">
            <div class="navbar-brand">JetBrains Servers</div>
            <div class="navbar-links">
                <a href="#valid-servers">有效服务器</a>
                <a href="#invalid-servers">无效服务器</a>
            </div>
        </div>
    </nav>
    
    <div class="hero-spacer"></div>
    <div class="container">
        <div class="header">
            <h1>JetBrains 激活服务器</h1>
            <div class="subtitle">实时监控和验证服务器状态</div>
            <div class="update-time">更新时间: {get_beijing_time()}</div>
        </div>
        
        <div class="stats-container">
            <div class="stats-card">
                <div class="stats-value">{total_servers}</div>
                <div class="stats-label">总服务器</div>
            </div>
            <div class="stats-card">
                <div class="stats-value" style="color: var(--success-color)">{len(valid_servers)}</div>
                <div class="stats-label">在线服务器</div>
            </div>
            <div class="stats-card">
                <div class="stats-value" style="color: var(--error-color)">{len(invalid_servers)}</div>
                <div class="stats-label">离线服务器</div>
            </div>
        </div>

        <div class="servers-section" id="valid-servers">
            <div class="section-badge">可用</div>
            <h2 class="section-title">有效服务器</h2>
            <ul class="server-list">
                {chr(10).join(f'''
                <li class="server-item valid">
                    <span class="server-url">{server}</span>
                    <button class="copy-btn" onclick="copyToClipboard(this, '{server}')">复制</button>
                </li>''' for server in valid_servers)}
            </ul>
        </div>

        <div class="servers-section" id="invalid-servers">
            <div class="section-badge">不可用</div>
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

    <footer class="footer">
        <p>⚡ 由 <strong>JetBrains Servers Updater</strong> 自动更新 | Made with cuijianzhuang ❤️</p>
    </footer>

    <div class="back-to-top" id="backToTop" title="返回顶部"></div>
        
    
    <script>
    async function copyToClipboard(button, text) {{
        try {{
            await navigator.clipboard.writeText(text);
            const originalText = button.textContent;
            
            // 添加复制成功反馈
            button.textContent = '已复制 ✓';
            button.classList.add('copied');
            
            // 添加触觉反馈（如果支持）
            if (navigator.vibrate) {{
                navigator.vibrate(50);
            }}
            
            setTimeout(() => {{
                button.textContent = originalText;
                button.classList.remove('copied');
            }}, 2000);
        }} catch (err) {{
            console.error('复制失败:', err);
            button.textContent = '失败 ✗';
            setTimeout(() => {{
                button.textContent = '复制';
            }}, 2000);
        }}
    }}

    // 添加键盘快捷键支持
    document.addEventListener('keydown', (e) => {{
        // Cmd/Ctrl + K 聚焦到第一个复制按钮
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {{
            e.preventDefault();
            const firstButton = document.querySelector('.copy-btn');
            if (firstButton) {{
                firstButton.focus();
                firstButton.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }}
        }}
    }});

    // 导航栏滚动效果和返回顶部按钮
    const navbar = document.querySelector('.navbar');
    const backToTop = document.getElementById('backToTop');
    const progressBar = document.getElementById('progressBar');
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {{
        const currentScroll = window.pageYOffset;
        
        // 导航栏效果
        if (currentScroll > 50) {{
            navbar.classList.add('scrolled');
        }} else {{
            navbar.classList.remove('scrolled');
        }}
        
        // 返回顶部按钮
        if (currentScroll > 300) {{
            backToTop.classList.add('show');
        }} else {{
            backToTop.classList.remove('show');
        }}
        
        // 进度条
        const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (currentScroll / windowHeight) * 100;
        progressBar.style.width = scrolled + '%';
        
        lastScroll = currentScroll;
    }});

    // 返回顶部点击事件
    backToTop.addEventListener('click', () => {{
        window.scrollTo({{
            top: 0,
            behavior: 'smooth'
        }});
    }});

    // 页面加载完成
    window.addEventListener('load', () => {{
        document.body.classList.add('loaded');
    }});

    // 页面加载后添加平滑滚动
    document.addEventListener('DOMContentLoaded', () => {{
        // 平滑滚动
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    const navHeight = navbar.offsetHeight;
                    const targetPosition = target.offsetTop - navHeight - 20;
                    window.scrollTo({{
                        top: targetPosition,
                        behavior: 'smooth'
                    }});
                }}
            }});
        }});

        // 滚动时元素淡入动画
        const observerOptions = {{
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        }};

        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }}
            }});
        }}, observerOptions);

        // 为服务器列表项添加观察
        document.querySelectorAll('.server-item').forEach((item, index) => {{
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            item.style.transition = `opacity 0.6s ease ${{index * 0.05}}s, transform 0.6s ease ${{index * 0.05}}s`;
            observer.observe(item);
        }});
    }});
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